// The page does no thinking. It sends what you type to /chat and draws
// whatever the recommendation agent does: every tool call as a row, every pick as a pin.

const COLOURS = ['#1a73e8', '#e8710a', '#188038', '#d93025', '#00897b', '#5f6368'];   // one per pick: pin, card and route share it
const TOUR = '#7b1fa2';                                // the legs of a walking tour
const MAP_TOOLS = ['geocode', 'nearby_places', 'walking_route'];
const session = crypto.randomUUID();

const map = L.map('map', { zoomControl: false }).setView([25, 0], 2);
L.control.zoom({ position: 'bottomright' }).addTo(map);

// Four looks for the map, picked from the box in the top corner. None needs a
// key. Tiles are not fetched while the map is flying somewhere, only once it
// lands, and a wider ring of them is kept so panning does not show grey.
const ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/';
const loading = { maxZoom: 19, updateWhenZooming: false, keepBuffer: 4 };
const MAPS = {
  Street: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { ...loading, attribution: '&copy; OpenStreetMap contributors' }),
  Light: L.tileLayer(ESRI + 'Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', { ...loading, maxNativeZoom: 16, attribution: 'Tiles &copy; Esri' }),
  Satellite: L.tileLayer(ESRI + 'World_Imagery/MapServer/tile/{z}/{y}/{x}', { ...loading, attribution: 'Tiles &copy; Esri' }),
  Terrain: L.tileLayer(ESRI + 'World_Topo_Map/MapServer/tile/{z}/{y}/{x}', { ...loading, attribution: 'Tiles &copy; Esri' }),
};
L.control.layers(MAPS, null, { position: 'topright', collapsed: false }).addTo(map);

// Open on the look this browser used last time.
let look = 'Street';
try { look = localStorage.getItem('atlas-map') || look; } catch (e) { /* storage is off */ }
(MAPS[look] || MAPS.Street).addTo(map);
map.on('baselayerchange', e => { try { localStorage.setItem('atlas-map', e.name); } catch (err) { /* storage is off */ } });

const youLayer = L.layerGroup().addTo(map);
const spotLayer = L.layerGroup().addTo(map);
const chat = document.getElementById('chat');
const input = document.getElementById('q');
const rows = {};      // open tool calls, by call id
const cards = {};     // the picks, by the description agent call that made them
let here = null;
let candidates = [];  // what nearby_places returned
let picked = [];      // the ones the recommendation agent chose
let routes = [];      // their walking routes, as lines on the map
let picks = {};       // pick and route are matched by the place's coordinates
let trips = {};
let kind = '';         // the kind of the last search, and the subtopics inside it
let subtopics = [];
let busy = false;

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const key = (lat, lon) => `${(+lat).toFixed(4)},${(+lon).toFixed(4)}`;
const far = m => m < 1000 ? `${m} m` : `${(m / 1000).toFixed(1)} km`;

function add(el) {
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
  return el;
}

function say(who, html) {
  const el = document.createElement('div');
  el.className = 'msg ' + who;
  el.innerHTML = html;
  return add(el);
}

function chips(labels, send) {
  const el = document.createElement('div');
  el.className = 'chips msg';
  for (const label of labels) {
    const b = document.createElement('button');
    b.textContent = label;
    b.onclick = () => {
      const text = send(label);
      if (text) ask(text);
    };
    el.appendChild(b);
  }
  return add(el);
}

// ---- talking to the agent ----

async function ask(text, shown = text) {
  if (busy) return;
  busy = true;
  document.querySelectorAll('.chips').forEach(c => c.remove());
  say('user', esc(shown));
  const thinking = say('agent', '<span class="thinking"><i></i><i></i><i></i></span>');

  try {
    const reply = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session, text }),
    });
    document.getElementById('instance').textContent = reply.headers.get('X-Atlas-Instance');
    const reader = reply.body.pipeThrough(new TextDecoderStream()).getReader();
    let buffer = '';
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += value;
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) if (line) draw(JSON.parse(line));
      chat.appendChild(thinking);
      chat.scrollTop = chat.scrollHeight;
    }
  } catch (e) {
    draw({ error: 'The server did not answer.' });
  }

  thinking.remove();
  busy = false;
  drawTour();
  if (here) offer();
}

// What to try next: narrow the last search to one subtopic, or pick a kind.
function offer() {
  const show = label => `Show me ${label.toLowerCase()} near me.`;
  if (subtopics.length > 1) chips(subtopics.map(s => 'Only ' + s), show);
  chips(['Food', 'Fun', 'Schools', 'More'], label => {
    if (label !== 'More') return show(label);
    chips(['Coffee', 'Shopping', 'Outdoors', 'Essentials'], show);
  });
}

function draw(step) {
  if (step.call) return onCall(step);
  if (step.result) return onResult(step);
  if (step.text) return say('agent', esc(step.text).replace(/\n/g, '<br>'));
  if (step.error) return say('agent error', esc(step.error));
}

// One row per tool call, tagged with how it reached the agent.
function onCall({ call, id, via, args }) {
  const el = document.createElement('div');
  el.className = 'ev wait ' + via;
  el.innerHTML = `<span class="tag">${via}</span><span><span class="call">${esc(call)}(${esc(Object.values(args).join(', '))})</span> <span class="out"></span> <span class="ms"></span></span>`;
  add(el);
  rows[id] = { el, t0: performance.now(), args };
  if (call === 'description_agent') pin(id, args.request);
  if (call === 'walking_route' && kind === 'essentials') pinEssential(id, args);
}

function onResult({ result, id, data }) {
  if (result === 'geocode' && data.found) arrive(data.lat, data.lon, data.name);
  if (result === 'nearby_places' && data.places) {
    kind = data.kind;
    subtopics = data.subtopics || [];
    scatter(data.places);
  }
  if (result === 'description_agent') tell(id, data);
  if (result === 'walking_route' && data.line) {
    const to = key(rows[id].args.to_lat, rows[id].args.to_lon);
    trips[to] = data;
    drawRoute(to);
  }

  const row = rows[id];
  if (!row) return;
  row.el.classList.remove('wait');
  row.el.querySelector('.out').textContent = '→ ' + summary(result, data);
  row.el.querySelector('.ms').textContent = ((performance.now() - row.t0) / 1000).toFixed(1) + ' s';
}

function summary(tool, data) {
  if (tool === 'list_skills') return 'on offer: ' + [...String(data).matchAll(/<name>\s*([^<\s]+)/g)].map(m => m[1]).join(', ');
  if (tool === 'load_skill') return 'instructions loaded';
  // A map tool that answers with plain text is reporting an error.
  if (typeof data === 'string' && MAP_TOOLS.includes(tool)) return 'failed: ' + data;
  if (tool === 'geocode') return data.found ? `${data.lat}, ${data.lon}` : 'no match';
  if (tool === 'nearby_places') return data.places ? `${data.count} places, nearest ${data.places.length} returned` : 'failed';
  if (tool === 'description_agent') return 'answered';
  if (tool === 'walking_route') return `${far(data.distance_m)}, ${data.minutes} min`;
  return 'done';
}

// ---- drawing on the map ----

function arrive(lat, lon, name) {
  const moved = !here || map.distance([here.lat, here.lon], [lat, lon]) > 50;
  here = { lat, lon };
  if (!moved) return;
  youLayer.clearLayers();
  spotLayer.clearLayers();
  L.circle([lat, lon], { radius: 600, color: '#1a73e8', weight: 1, fillOpacity: 0.05 }).addTo(youLayer);
  L.marker([lat, lon], { icon: L.divIcon({ className: '', html: '<div class="you"></div>', iconSize: [18, 18] }), zIndexOffset: 1000 })
    .addTo(youLayer).bindPopup(esc(name));
  map.flyTo([lat, lon], 16, { duration: 1.2 });
}

// Everything the recommendation agent had to choose from, as small grey dots.
function scatter(places) {
  spotLayer.clearLayers();
  candidates = places;
  picked = [];
  routes = [];
  picks = {};
  trips = {};
  for (const p of places) {
    // Hovering shows what the listing already knows, which costs nothing.
    // Describing a place costs a model call, so that waits for a click.
    const facts = `<b>${esc(p.name)}</b><br>${esc(p.type.replace(/_/g, ' '))} &middot; ${far(p.distance_m)} away`;
    const dot = L.circleMarker([p.lat, p.lon], { radius: 6, color: '#fff', weight: 1.5, fillColor: '#9aa0a6', fillOpacity: 1 })
      .addTo(spotLayer)
      .bindTooltip(facts)
      .bindPopup(`${facts}<br><button class="add">Add to my picks</button>`);
    dot.on('popupopen', e => {
      e.popup.getElement().querySelector('.add').onclick = () => { map.closePopup(); addPick(p); };
    });
  }
}

// Ask the recommendation agent to treat one more place like its own picks. The page spells
// out the listing, so the agent does not have to remember it.
function addPick(p) {
  if (picked.includes(p)) return;
  const listing = [p.name, p.type, p.cuisine, p.address, `latitude ${p.lat}`, `longitude ${p.lon}`].filter(Boolean).join(', ');
  ask(`Add this place to my picks: ${listing}. I am at latitude ${here.lat}, longitude ${here.lon}.`, `Add ${p.name} to my picks.`);
}

// The recommendation agent asked the description agent about a place, so it is one of the picks.
// It gets a pin, a card and a walking route now; the description follows.
function pin(id, request) {
  const spot = candidates
    .filter(p => request.includes(p.name))
    .sort((a, b) => b.name.length - a.name.length)[0];
  if (spot) pick(spot, id, '<span class="thinking"><i></i><i></i><i></i></span>');
}

// Essentials get no description, so there is no description_agent call to pin them.
// The route request is the sign that the recommendation agent picked one.
function pinEssential(id, args) {
  const spot = candidates.find(p => key(p.lat, p.lon) === key(args.to_lat, args.to_lon));
  if (spot) pick(spot, id, '');
}

function pick(spot, id, story) {
  if (picked.includes(spot)) return;   // a follow-up about a place already shown
  picked.push(spot);
  const n = picked.length;
  const colour = COLOURS[(n - 1) % COLOURS.length];

  const marker = L.marker([spot.lat, spot.lon], {
    icon: L.divIcon({ className: '', html: `<div class="pin" style="background:${colour}"><span>${n}</span></div>`, iconSize: [28, 28], iconAnchor: [14, 28] }),
    zIndexOffset: 500,
  }).addTo(spotLayer).bindPopup(`<b>${esc(spot.name)}</b><div class="links">${links(spot)}</div>`, { maxWidth: 300, offset: [0, -22] });

  const card = document.createElement('div');
  card.className = 'card';
  card.style.setProperty('--colour', colour);
  card.innerHTML = `
    <div class="num">${n}</div>
    <div>
      <h3>${esc(spot.name)}</h3>
      <div class="meta">${esc(spot.type.replace(/_/g, ' '))} &middot; <span class="trip">${far(spot.distance_m)} away</span></div>
      ${spot.address ? `<div class="meta">${esc(spot.address)}</div>` : ''}
      ${spot.opening_hours ? `<div class="meta">Open ${esc(spot.opening_hours)}</div>` : ''}
      <p class="story">${story}</p>
      <div class="sources"></div>
      <div class="links">${links(spot)}</div>
    </div>`;
  card.onclick = e => {
    if (e.target.closest('a')) return;
    document.querySelectorAll('.card.on').forEach(c => c.classList.remove('on'));
    card.classList.add('on');
    map.flyTo([spot.lat, spot.lon], 17, { duration: 0.8 });
    marker.openPopup();
  };
  add(card);
  cards[id] = { card, marker, spot };

  picks[key(spot.lat, spot.lon)] = { n, colour, card };
  drawRoute(key(spot.lat, spot.lon));
  frame();
}

// Keep you and every pick in view. Picks and routes arrive in a burst, so
// wait for the burst to end and move the map once, not six times.
let framing;
function frame() {
  clearTimeout(framing);
  framing = setTimeout(() => {
    map.flyToBounds([[here.lat, here.lon], ...picked.map(p => [p.lat, p.lon])], { padding: [80, 80], maxZoom: 17, duration: 0.8 });
  }, 500);
}

// Facts straight from the map listing, never from the model.
function links(spot) {
  const out = [];
  if (spot.website) {
    const url = /^https?:\/\//.test(spot.website) ? spot.website : 'https://' + spot.website;
    out.push(`<a href="${esc(url)}" target="_blank" rel="noopener">Website</a>`);
  }
  const directions = `https://www.google.com/maps/dir/?api=1&origin=${here.lat},${here.lon}&destination=${spot.lat},${spot.lon}&travelmode=walking`;
  out.push(`<a href="${directions}" target="_blank" rel="noopener">Directions</a>`);
  if (spot.phone) out.push(`<a href="tel:${esc(spot.phone.replace(/[^+\d]/g, ''))}">${esc(spot.phone)}</a>`);
  return out.join('');
}

// A pick's walking route, in the pick's colour, labelled with its length and
// time. The route comes from the walking_route tool, so it is drawn once both
// the pick and its route have arrived, in whichever order.
// Routes often leave along the same street, so each is a different width and
// the widest goes underneath: where they overlap you still see every colour.
function drawRoute(key) {
  const pick = picks[key], trip = trips[key];
  if (!pick || !trip || pick.drawn) return;
  pick.drawn = true;

  const label = `${far(trip.distance_m)} &middot; ${trip.minutes} min walk`;
  const line = L.polyline(decode(trip.line), { color: pick.colour, weight: Math.max(4, 14 - 3 * pick.n) })
    .addTo(spotLayer)
    .bindTooltip(`<b style="color:${pick.colour}">${pick.n} &middot; ${label}</b>`, { permanent: true, direction: 'center', className: 'trip-label' });
  routes.push(line);
  routes.sort((a, b) => b.options.weight - a.options.weight).forEach(r => r.bringToFront());
  pick.card.querySelector('.trip').innerHTML = label;
  frame();
}

// A walking tour has no cards. The skill plans it leg by leg with
// walking_route and writes the tour as text, so any route that no pick
// claimed is a leg of the tour: draw them in order, numbered at each stop.
function drawTour() {
  const legs = Object.keys(trips).filter(to => !picks[to] && !trips[to].drawn);
  if (!legs.length) return;
  const drawn = legs.map((to, i) => {
    const trip = trips[to];
    trip.drawn = true;
    const path = decode(trip.line);
    L.marker(path[path.length - 1], {
      icon: L.divIcon({ className: '', html: `<div class="pin" style="background:${TOUR}"><span>${i + 1}</span></div>`, iconSize: [28, 28], iconAnchor: [14, 28] }),
      zIndexOffset: 500,
    }).addTo(spotLayer);
    return L.polyline(path, { color: TOUR, weight: 6 })
      .addTo(spotLayer)
      .bindTooltip(`<b style="color:${TOUR}">leg ${i + 1} &middot; ${far(trip.distance_m)} &middot; ${trip.minutes} min</b>`, { permanent: true, direction: 'center', className: 'trip-label' });
  });
  map.flyToBounds(L.featureGroup(drawn).getBounds(), { padding: [80, 80], maxZoom: 17, duration: 0.8 });
}

// Map services pack a route into a short string, an "encoded polyline".
// This unpacks it into [lat, lon] points.
function decode(packed) {
  const points = [];
  let at = 0, lat = 0, lon = 0;
  const next = () => {
    let shift = 0, value = 0, byte;
    do {
      byte = packed.charCodeAt(at++) - 63;
      value |= (byte & 31) << shift;
      shift += 5;
    } while (byte >= 32);
    return value & 1 ? ~(value >> 1) : value >> 1;
  };
  while (at < packed.length) {
    lat += next();
    lon += next();
    points.push([lat / 1e5, lon / 1e5]);
  }
  return points;
}

// The description agent's answer: the description, then the pages it was checked against.
function tell(id, answer) {
  const pick = cards[id];
  if (String(answer).includes('RESOURCE_EXHAUSTED')) answer = 'The description agent was rate limited. Ask again in a moment.';
  const [text, sources = ''] = String(answer).split(/\s*Sources:\s*/);
  const story = esc(text.trim().replace(/\*+/g, '')).replace(/\n+/g, '<br>');
  const pages = sources.split('\n').filter(line => line.includes(' http')).map(line => {
    const cut = line.lastIndexOf(' http');
    return `<a href="${esc(line.slice(cut + 1))}" target="_blank" rel="noopener">${esc(line.slice(0, cut))}</a>`;
  });

  const checked = pages.length ? 'Checked against ' + pages.join(', ') : '';
  if (!pick) return say('agent', `${story}<div class="sources">${checked}</div>`);   // a follow-up answer

  pick.card.querySelector('.story').innerHTML = story;
  pick.card.querySelector('.sources').innerHTML = checked;
  pick.marker.setPopupContent(`<b>${esc(pick.spot.name)}</b><p>${story}</p><div class="links">${links(pick.spot)}</div>`);
}

// ---- input ----

function shareLocation() {
  if (!navigator.geolocation) return say('agent', "This browser can't share a location. Type a place instead.");
  navigator.geolocation.getCurrentPosition(
    pos => {
      const lat = +pos.coords.latitude.toFixed(5), lon = +pos.coords.longitude.toFixed(5);
      arrive(lat, lon, 'You are here');
      ask(`I'm at latitude ${lat}, longitude ${lon}.`, "I'm here.");
    },
    () => say('agent', "I couldn't read your location. Type a place instead."),
    { timeout: 8000 },
  );
}

document.getElementById('ask').onsubmit = e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  ask(text);
};
document.getElementById('here').onclick = shareLocation;

say('agent', 'Where are you? Share your location or type a place.');
chips(['Grand Central Market, Los Angeles', 'Shibuya Crossing, Tokyo', 'Marina Beach, Chennai'], place => `I'm at ${place}.`);

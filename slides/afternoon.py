"""Afternoon deck: taking an agent to production on Google Cloud. Run: python afternoon.py"""

from parts import *


def source(s, text):
    """A small grey source line above the footer."""
    txt(s, MARGIN, Inches(6.0), SW - MARGIN * 2, Inches(0.3), text, size=T_MICRO, color=INK3)


def rows(s, items, top=Inches(1.95), left=Inches(4.4)):
    """A stack of full-width bands: bold label on the left, plain text on the right."""
    for i, (what, detail, fill, tcol) in enumerate(items):
        y = top + Inches(0.82) * i
        box(s, MARGIN, y, SW - MARGIN * 2, Inches(0.68), fill=fill)
        txt(s, MARGIN + Inches(0.35), y + Inches(0.19), left - Inches(0.5), Inches(0.35), what, size=T_BODY, color=tcol, bold=True)
        txt(s, MARGIN + left, y + Inches(0.19), SW - MARGIN * 2 - left - Inches(0.3), Inches(0.35), detail, size=T_BODY, color=INK2)


def cover(s):
    gdots(s, MARGIN, Inches(0.72))
    eyebrow(s, MARGIN, Inches(1.5), "Afternoon session   ·   two hours   ·   hands on", col=INK3)
    rich(s, MARGIN, Inches(2.0), Inches(11.6), Inches(2.6),
         [[("Auto-scale your AI agent", True, INK)],
          [("on Cloud Run", False, INK)]], size=T_DISPLAY, spacing=1.1)
    txt(s, MARGIN, Inches(3.75), Inches(11), Inches(1.0),
        "Where to run an agent on Google Cloud, how it scales,\nand what breaks when real people show up.",
        size=T_H2, color=INK2, spacing=1.4)
    txt(s, MARGIN, Inches(5.7), Inches(8), Inches(0.4), "Kiruthika Subramani", size=T_H2, color=INK, bold=True)
    txt(s, MARGIN, Inches(6.15), Inches(8), Inches(0.3), "Data Scientist, Bell Canada   ·   Google Developer Expert in AI",
        size=T_SMALL, color=INK3)
    return ("Welcome back. This morning was about what an agent is. This afternoon is about what "
            "happens after the demo: where you run it, how it copes with a crowd, how you keep it "
            "safe, and what it costs. Ideas first, then we deploy one live.")


def hello(s):
    pw = Inches(4.5)
    ph = s.shapes.add_picture(str(ASSETS / "kiruthika.jpg"), 0, 0, width=pw, height=SH)
    ph.crop_left, ph.crop_right = 0.12, 0.12
    tx = pw + Inches(0.85)
    eyebrow(s, tx, Inches(1.32), "Rebonjour")
    txt(s, tx, Inches(1.68), Inches(7.2), Inches(0.7), "Still Kiruthika", size=T_DISPLAY, color=INK, bold=True)
    txt(s, tx, Inches(2.42), Inches(7.4), Inches(0.36),
        "Starbucks still writes Cindy. Lunch did not change that.", size=T_BODY, color=INK3)
    rich(s, tx, Inches(3.12), Inches(7.4), Inches(2.4),
         [[("From ", False, INK2), ("Montreal", True, INK)],
          [("Data Scientist at ", False, INK2), ("Bell Canada", True, INK)],
          [("Google Developer Expert", True, INK), (" in AI", False, INK2)],
          [("Mila", True, INK), (" alumni, Women in AI scholarship", False, INK2)],
          [("Wrote ", False, INK2), ("two books", True, INK)]],
         size=T_H2, spacing=1.42)
    txt(s, tx, Inches(6.1), Inches(7.4), Inches(0.4), "Spider Man fan. Nice person.", size=T_H2, color=BLUE)
    return ("For anyone who joined after lunch, I am Kiruthika, still Cindy at Starbucks. Data "
            "scientist at Bell Canada, Google Developer Expert. This morning we built an agent. "
            "This afternoon we do the part nobody puts in the demo video: making it survive "
            "other people.")


def laptop(s):
    statement(s, "Where we left it",
              [[("It works on my laptop.", False, INK)],
               [("That was the easy part.", True, BLUE)]],
              "One process. One machine. One user, and it was me.")
    return ("It works on my laptop. The most expensive sentence in software. One process, one "
            "machine, one user. Everything this afternoon is about what changes when that is no "
            "longer true.")


def what_changes(s):
    head(s, "Production", "Four things that are different with real users")
    items = [("Many at once", "requests arrive together, not one after another", BLUE_L, BLUE, BLUE_D),
             ("No shared memory", "the second message may reach a different copy of your app", RED_L, RED, RED),
             ("Things fail", "the model is busy, an API says no, a machine restarts", YEL_L, YEL, INK),
             ("Every call costs", "tokens, searches and compute, multiplied by every user", GRN_L, GRN, GRN)]
    w, gap = Inches(2.75), Inches(0.3)
    for i, (name, body, fill, line, tcol) in enumerate(items):
        x = MARGIN + (w + gap) * i
        box(s, x, Inches(2.05), w, Inches(3.4), fill=fill, line=line, lw=1.25)
        txt(s, x + Inches(0.3), Inches(2.45), w - Inches(0.6), Inches(0.9), name, size=22, color=tcol, bold=True, spacing=1.05)
        txt(s, x + Inches(0.3), Inches(3.75), w - Inches(0.6), Inches(1.4), body, size=T_BODY, color=INK2, spacing=1.35)
    takeaway(s, [("None of these show up in a demo. ", False), ("All of them show up in week one.", True)])
    return ("Four things change. Requests arrive at the same moment. Your app runs as several "
            "copies, so the second message from a user may land on a copy that never saw the "
            "first. Things fail: the model is busy, an API refuses, a machine restarts. And every "
            "call costs money, multiplied by every user. None of it is visible in a demo.")


def options(s):
    head(s, "Where to run it", "Three homes for an agent on Google Cloud")
    w, gap = Inches(3.75), Inches(0.33)
    homes = [("Agent Engine", "the managed runtime", "You hand over the agent. Sessions, memory and tracing come built in.", BLUE_L, BLUE, BLUE_D),
             ("Cloud Run", "serverless containers", "You hand over a container. It scales with traffic, down to zero.", GRN_L, GRN, GRN),
             ("GKE", "Kubernetes", "You run the cluster. Full control, sandboxes, your own GPUs.", YEL_L, YEL, INK)]
    for i, (name, kind, body, fill, line, tcol) in enumerate(homes):
        x = MARGIN + (w + gap) * i
        box(s, x, Inches(2.05), w, Inches(3.4), fill=fill, line=line, lw=1.25)
        txt(s, x + Inches(0.32), Inches(2.4), w - Inches(0.64), Inches(0.6), name, size=28, color=tcol, bold=True)
        txt(s, x + Inches(0.32), Inches(3.15), w - Inches(0.64), Inches(0.4), kind, size=T_BODY, color=INK, bold=True)
        txt(s, x + Inches(0.32), Inches(3.75), w - Inches(0.64), Inches(1.5), body, size=T_BODY, color=INK2, spacing=1.4)
    takeaway(s, [("Left to right: ", False), ("less to manage, then more to control.", True)])
    return ("On Google Cloud an agent has three natural homes. Agent Engine is the managed runtime: "
            "you hand over the agent and it brings sessions, memory and tracing. Cloud Run takes "
            "a container and scales it with traffic, down to zero. GKE is Kubernetes: you run "
            "the cluster and you get full control. Read it left to right as less to manage, then "
            "more to control.")


def which_one(s):
    head(s, "Where to run it", "When to choose which")
    rows(s, [
        ("A chat or API agent, bursty traffic", "Cloud Run. Start here.", GRN_L, GRN),
        ("You want sessions, memory and evals managed", "Agent Engine", BLUE_L, BLUE_D),
        ("Long batch work, no user waiting", "Cloud Run jobs", GRN_L, GRN),
        ("The agent runs code it wrote itself", "GKE, in a sandbox", YEL_L, INK),
        ("A fleet of agents, or your own models on GPUs", "GKE", YEL_L, INK),
    ], left=Inches(6.6))
    takeaway(s, [("The same agent code can move between them. ", False), ("Pick the simplest that fits.", True)])
    return ("So which one. If it is a chat or an API with bursty traffic, start with Cloud Run. If "
            "you would rather not build session storage, memory and evaluation yourself, Agent "
            "Engine. Long batch work with nobody waiting, Cloud Run jobs. If the agent executes "
            "code it wrote, you want a sandbox, and that points to GKE. Same for a fleet of agents "
            "or your own models on GPUs. The agent code moves between them, so choose the simplest "
            "one that fits today.")


def container(s):
    head(s, "Packaging", "A container is a recipe anyone can run")
    code(s, MARGIN, Inches(1.95), Inches(6.6), Inches(3.9),
         "FROM python:3.13-slim\n"
         "WORKDIR /app\n"
         "\n"
         "COPY requirements.txt .\n"
         "RUN pip install -r requirements.txt\n"
         "\n"
         "COPY . .\n"
         "\n"
         "CMD [\"sh\", \"serve.sh\"]")
    x = MARGIN + Inches(7.0)
    points = [("Same everywhere", "your laptop, a colleague's, the cloud", BLUE_L, BLUE_D),
              ("Dependencies before code", "a code change does not reinstall them", YEL_L, INK),
              ("No secrets inside", "keys stay out; the platform signs the calls", GRN_L, GRN)]
    for i, (title, sub, fill, tcol) in enumerate(points):
        yy = Inches(1.95) + Inches(1.34) * i
        box(s, x, yy, Inches(4.9), Inches(1.16), fill=fill)
        txt(s, x + Inches(0.3), yy + Inches(0.2), Inches(4.4), Inches(0.35), title, size=T_BODY, color=tcol, bold=True)
        txt(s, x + Inches(0.3), yy + Inches(0.62), Inches(4.4), Inches(0.3), sub, size=T_SMALL, color=INK2)
    takeaway(s, [("If it runs in the container here, ", False), ("it runs in the container there.", True)])
    return ("Whichever home you choose, you will probably ship a container. A Dockerfile is a "
            "recipe. Start from a small Linux with Python. Install the dependencies before "
            "copying the code, so a one line change does not reinstall the world. Say what to "
            "run. And notice there is no API key in it. In the cloud the platform's own identity "
            "signs the calls to the model.")


def how_it_scales(s):
    head(s, "Scaling", "How Cloud Run decides to add copies")
    y = Inches(2.2)
    for i in range(8):
        oval(s, MARGIN + Inches(0.35) + Inches(0.42) * (i % 4), y + Inches(0.3) + Inches(0.42) * (i // 4), Inches(0.14), BLUE)
    txt(s, MARGIN, y + Inches(1.25), Inches(2.2), Inches(0.3), "requests arriving", size=T_SMALL, color=INK2)
    arrow(s, MARGIN + Inches(2.3), y + Inches(0.5), MARGIN + Inches(3.3), y + Inches(0.5), col=INK2, w=2)
    for i in range(3):
        node(s, MARGIN + Inches(3.5) + Inches(1.75) * i, y, Inches(1.55), Inches(1.0), f"Instance {i + 1}",
             fill=GRN_L if i < 2 else GREY_L, tcol=GRN if i < 2 else INK3, tsize=T_SMALL)
    txt(s, MARGIN + Inches(3.5), y + Inches(1.25), Inches(7), Inches(0.3),
        "each takes a few at a time; a new one starts when they are full", size=T_SMALL, color=INK2)
    w, gap = Inches(2.75), Inches(0.3)
    facts = [("Concurrency", "requests one instance\nhandles at once"), ("Max instances", "the ceiling, and the cap\non your bill"),
             ("Min instances", "zero is free when idle,\nand slow on the first request"), ("Cold start", "the wait while a new\ninstance boots")]
    for i, (name, body) in enumerate(facts):
        x = MARGIN + (w + gap) * i
        box(s, x, Inches(4.2), w, Inches(1.45), fill=GREY_L)
        txt(s, x + Inches(0.28), Inches(4.38), w - Inches(0.56), Inches(0.35), name, size=T_BODY, color=INK, bold=True)
        txt(s, x + Inches(0.28), Inches(4.8), w - Inches(0.56), Inches(0.8), body, size=T_SMALL, color=INK2, spacing=1.3)
    takeaway(s, [("Concurrency × max instances = ", False), ("how many people fit in the room.", True)])
    return ("How does Cloud Run scale. Each instance takes a few requests at a time. That number is "
            "concurrency. When the running instances are full, it starts another, up to max "
            "instances, which is your ceiling and also the cap on your bill. With min instances "
            "at zero you pay nothing when idle, and the first visitor waits for an instance to "
            "boot. That wait is a cold start. Multiply concurrency by max instances and you know "
            "how many people fit in the room.")


def agents_are_different(s):
    head(s, "Scaling", "Why agents scale differently from websites")
    half = (SW - MARGIN * 2 - Inches(0.4)) / 2
    card(s, MARGIN, Inches(2.0), half, Inches(3.4), "A web page",
         "answers in milliseconds\n\n"
         "one instance serves hundreds at once\n\n"
         "the slow part is your own code",
         fill=GREY_L)
    card(s, MARGIN + half + Inches(0.4), Inches(2.0), half, Inches(3.4), "An agent turn",
         "holds the request open for many seconds\n\n"
         "so concurrency per instance stays low\n\n"
         "the slow part is the model, which you do not run",
         fill=BLUE_L, line=BLUE, tcol=BLUE_D)
    takeaway(s, [("Adding instances does not help ", False), ("if the model is the one saying wait.", True)])
    return ("Agents do not scale like websites. A page answers in milliseconds, so one instance "
            "serves hundreds of people. One agent turn holds a request open for ten or twenty "
            "seconds while the model works and tools run, so each instance can only take a few. "
            "And the slowest part is the model, which you do not run. You can add all the "
            "instances you like. If the model provider says wait, everyone waits.")


def state(s):
    head(s, "State", "The bug with no error message")
    node(s, MARGIN, Inches(3.05), Inches(2.2), Inches(1.3), "Asha", "one chat, two messages", fill=GREY_L, tsize=T_H2)
    ax = MARGIN + Inches(6.6)
    node(s, ax, Inches(2.0), Inches(5.3), Inches(1.45), "Instance A", "\"Asha. Got it.\"   kept in its own memory",
         fill=GRN_L, line=GRN, tcol=GRN, tsize=T_H2)
    node(s, ax, Inches(4.0), Inches(5.3), Inches(1.45), "Instance B", "\"I don't know your name.\"   never met her",
         fill=RED_L, line=RED, tcol=RED, tsize=T_H2)
    arrow(s, MARGIN + Inches(2.25), Inches(3.5), ax - Inches(0.05), Inches(2.72), col=INK2, w=2)
    arrow(s, MARGIN + Inches(2.25), Inches(3.9), ax - Inches(0.05), Inches(4.72), col=INK2, w=2)
    txt(s, MARGIN + Inches(2.9), Inches(2.45), Inches(3.4), Inches(0.3), "1.  \"Hi, my name is Asha.\"", size=T_SMALL, color=INK2)
    txt(s, MARGIN + Inches(2.9), Inches(4.75), Inches(3.4), Inches(0.3), "2.  \"What is my name?\"", size=T_SMALL, color=INK2)
    takeaway(s, [("Each instance keeps its own diary. ", False), ("Nobody shares.", True)])
    return ("Here is the bug that never raises an error. Asha's first message reaches one instance, "
            "which remembers her in its own memory. Her second message reaches another instance, "
            "which has never heard of her. Nothing crashes. No log line. She is simply forgotten. "
            "With one instance you never see it. With several you see it most of the time.")


def shared_state(s):
    head(s, "State", "Move the memory out of the instance")
    for i in range(3):
        node(s, MARGIN + Inches(0.3) + Inches(2.1) * i, Inches(2.1), Inches(1.85), Inches(1.0), f"Instance {i + 1}", fill=GREY_L, tsize=T_SMALL)
        arrow(s, MARGIN + Inches(1.22) + Inches(2.1) * i, Inches(3.12), MARGIN + Inches(3.3), Inches(4.05))
    node(s, MARGIN + Inches(1.6), Inches(4.1), Inches(3.5), Inches(1.3), "A shared store", "Firestore, a database, managed sessions",
         fill=BLUE, tcol=WHITE, tsize=T_H2)
    x = Inches(7.6)
    box(s, x, Inches(2.05), Inches(5.0), Inches(3.4), fill=GRN_L)
    txt(s, x + Inches(0.35), Inches(2.3), Inches(4.3), Inches(0.3), "FROM OUR REHEARSAL, 20 USERS AT ONCE", size=T_MICRO, color=INK3, bold=True)
    rich(s, x + Inches(0.35), Inches(2.75), Inches(4.3), Inches(1.9),
         [[("3 of 20", True, RED), ("  remembered", False, INK2)],
          [("memory inside the instance", False, INK2)],
          [("19 of 20", True, GRN), ("  remembered", False, INK2)],
          [("memory in Firestore", False, INK2)]],
         size=20, spacing=1.25)
    txt(s, x + Inches(0.35), Inches(4.85), Inches(4.3), Inches(0.5), "The twentieth request was refused\nat the instance ceiling.",
        size=T_SMALL, color=INK2, spacing=1.3)
    takeaway(s, [("Instances that hold nothing ", False), ("can be added and removed freely.", True)])
    return ("The fix is to move the memory out of the instance into a store they all share: "
            "Firestore, a database, or the managed sessions that Agent Engine gives you. Real "
            "numbers from my rehearsal, twenty users at once. With memory inside the instance, "
            "three of twenty were remembered. With Firestore, nineteen. The twentieth was a "
            "request the platform refused because the room was full. Once instances hold nothing, "
            "the platform can add and remove them freely.")


def challenges(s):
    head(s, "What goes wrong", "Five things that bite when you scale an agent")
    rows(s, [
        ("Model rate limits", "429 from the provider: add retries, or reserve capacity", RED_L, RED),
        ("Cold starts", "the first user after a quiet spell waits for a boot", YEL_L, INK),
        ("Long requests", "one turn can outlast a timeout: stream progress back", YEL_L, INK),
        ("Other people's APIs", "free services throttle or block shared cloud addresses", YEL_L, INK),
        ("The ceiling", "at max instances, new requests are refused", GREY_L, INK),
    ])
    takeaway(s, [("We met four of the five ", False), ("rehearsing this workshop.", True)])
    return ("Five things that bite. The model provider rate limits you, so you need retries or "
            "reserved capacity. Cold starts make the first user wait. A single turn can outlast a "
            "timeout, so stream progress back. Free third party APIs throttle or block traffic "
            "from shared cloud addresses. And at max instances, new requests are refused. I met "
            "four of these five rehearsing this workshop: rate limits, cold starts, a blocked "
            "API and the ceiling.")


def safe_deploy(s):
    head(s, "Safety", "Deploying it without regretting it")
    habits = [("Private by default", "nobody calls it without\nproving who they are"),
              ("No secrets in the image", "use the platform's identity,\nnot a pasted key"),
              ("A narrow service account", "it can call the model and the\ndatabase, and nothing else"),
              ("A ceiling and a budget alert", "max instances caps the spend,\nthe alert tells you first"),
              ("Guard input and output", "check what comes in, and\nwhat the agent wants to do"),
              ("Trace every step", "which tool, how long,\nhow many tokens")]
    w, h, gx, gy = Inches(3.75), Inches(1.75), Inches(0.33), Inches(0.28)
    fills = [BLUE_L, GRN_L, YEL_L, RED_L, GREY_L, BLUE_L]
    for i, (name, body) in enumerate(habits):
        x = MARGIN + (w + gx) * (i % 3)
        y = Inches(1.95) + (h + gy) * (i // 3)
        box(s, x, y, w, h, fill=fills[i])
        txt(s, x + Inches(0.3), y + Inches(0.24), w - Inches(0.6), Inches(0.4), name, size=T_BODY, color=INK, bold=True)
        txt(s, x + Inches(0.3), y + Inches(0.72), w - Inches(0.6), Inches(0.9), body, size=T_SMALL, color=INK2, spacing=1.35)
    takeaway(s, [("A public URL is ", False), ("a public wallet.", True)])
    return ("Safety, the deployment version. Private by default, so nobody calls it without "
            "proving who they are. No secrets baked into the image. A service account that can "
            "reach the model and the database and nothing else. A max instances ceiling and a "
            "budget alert, because a public URL is a public wallet. Guardrails on what comes in "
            "and on what the agent wants to do. And traces of every step.")


def watch(s):
    head(s, "Operations", "What to watch once it is live")
    w, gap = Inches(2.75), Inches(0.3)
    dials = [("Latency per step", "which tool or model call is the slow one", BLUE_L, BLUE_D),
             ("Tokens per turn", "your cost, and an early sign of a bloated context", YEL_L, INK),
             ("Tool error rate", "an API that started saying no", RED_L, RED),
             ("Instance count", "are you near the ceiling at peak", GRN_L, GRN)]
    for i, (name, body, fill, tcol) in enumerate(dials):
        x = MARGIN + (w + gap) * i
        box(s, x, Inches(2.05), w, Inches(3.0), fill=fill)
        txt(s, x + Inches(0.3), Inches(2.4), w - Inches(0.6), Inches(0.9), name, size=22, color=tcol, bold=True, spacing=1.05)
        txt(s, x + Inches(0.3), Inches(3.65), w - Inches(0.6), Inches(1.2), body, size=T_BODY, color=INK2, spacing=1.35)
    takeaway(s, [("An average hides everything. ", False), ("Look at the slowest one in twenty.", True)])
    return ("Once it is live, four dials. Latency per step, so you know whether the model or a "
            "tool is the slow one. Tokens per turn, which is your cost and an early warning that "
            "the context is bloating. Tool error rate, because someone else's API will start "
            "refusing you one day. And instance count against your ceiling. One tip: never trust "
            "the average. Look at the slowest request in twenty.")


def cost(s):
    head(s, "Money", "What you actually pay for")
    rows(s, [
        ("Nothing while idle", "scaled to zero: no requests, no instances, no charge", GRN_L, GRN),
        ("Instance time", "only while requests are being served", GREY_L, INK),
        ("Model tokens", "every step the agent takes, input and output", GREY_L, INK),
        ("Search grounding", "billed per grounded request, on top of tokens", RED_L, RED),
        ("Storage", "a few small writes per conversation", GREY_L, INK),
    ])
    takeaway(s, [("Load test with a cheap question. ", False), ("Never with the expensive one.", True)])
    return ("Money. Scaled to zero, you pay nothing while nobody is using it. You pay for instance "
            "time while serving, for model tokens on every step, for search grounding per request "
            "where you use it, and a little for storage. A practical rule: when you load test, "
            "send a cheap question. The load test should stress your infrastructure, not your "
            "credit card.")


def open_problems(s):
    head(s, "The honest slide", "What everyone is still working out")
    rows(s, [
        ("Evaluation", "how to test something that answers differently each time", BLUE_L, BLUE_D),
        ("Capacity", "your limit is often the model provider's, not your own", YEL_L, INK),
        ("Identity", "which agent is calling, on whose behalf, with what rights", RED_L, RED),
        ("Predictable cost", "one long session can cost as much as many short ones", YEL_L, INK),
        ("Security", "injection, tool misuse, agents trusting other agents", RED_L, RED),
    ])
    source(s, "Security categories follow the OWASP Top 10 for Agentic Applications 2026")
    return ("And the honest slide. Things the whole industry is still working out. How do you "
            "evaluate something that answers differently each time. Capacity, because your real "
            "limit is often the model provider's. Identity: which agent is calling, for which "
            "user, with which rights. Cost you can predict. And security, where OWASP now has a "
            "top ten just for agents. If you are stuck on one of these, so is everyone else.")


def checklist(s):
    head(s, "Before you open the door", "A checklist you can reuse")
    left = ["A container, with no secrets inside", "Chats live in a shared store",
            "Concurrency and max instances set on purpose", "Retries around model and tool calls"]
    right = ["Private, or behind real sign in", "A budget alert that someone reads",
             "Every tool call is traced", "Load tested with a cheap question"]
    half = (SW - MARGIN * 2 - Inches(0.4)) / 2
    for col, items in enumerate((left, right)):
        x = MARGIN + (half + Inches(0.4)) * col
        for i, item in enumerate(items):
            y = Inches(2.0) + Inches(0.95) * i
            box(s, x, y, half, Inches(0.78), fill=GREY_L)
            oval(s, x + Inches(0.45), y + Inches(0.39), Inches(0.13), GRN)
            txt(s, x + Inches(0.8), y + Inches(0.24), half - Inches(1.0), Inches(0.35), item, size=T_BODY, color=INK)
    takeaway(s, [("Eight lines. ", False), ("Now let us tick them off live.", True)])
    return ("Eight lines to take home. Container with no secrets. Chats in a shared store. "
            "Concurrency and max instances chosen on purpose. Retries. Private or behind real "
            "sign in. A budget alert somebody actually reads. Traces. And a load test with a "
            "cheap question. Now let us go and tick them off on a real service.")


def close(s):
    gdots(s, MARGIN, Inches(0.9))
    eyebrow(s, MARGIN, Inches(1.72), "Thank you")
    rich(s, MARGIN, Inches(2.18), Inches(11.8), Inches(1.6),
         [[("A container makes it portable.", False, INK)],
          [("A platform makes it elastic.", False, INK)]], size=T_DISPLAY, spacing=1.1)
    txt(s, MARGIN, Inches(4.15), Inches(11.5), Inches(0.6), "A shared store makes it remember your name.",
        size=T_H1, color=BLUE)
    txt(s, MARGIN, Inches(5.5), Inches(11), Inches(0.9),
        "Delete what you deployed before you leave.\nYour credit card will thank you.",
        size=T_H2, color=INK2, spacing=1.35)
    return ("That is the afternoon. A container makes your agent portable. A platform makes it "
            "elastic. A shared store makes it remember your name whichever copy answers. One last "
            "thing before you leave: delete what you deployed. Thank you.")


SLIDES = [cover, hello, laptop, what_changes, options, which_one, container, how_it_scales,
          agents_are_different, state, shared_state, challenges, safe_deploy, watch, cost,
          open_problems, checklist, close]

if __name__ == "__main__":
    build_deck(HERE / "Agents-Afternoon.pptx", SLIDES, no_footer=("cover", "hello", "close"))

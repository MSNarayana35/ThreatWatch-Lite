from typing import List
from datetime import datetime
import re
import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..dependencies import get_db
from .auth import get_current_user
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/ctf",
    tags=["ctf"],
    responses={404: {"description": "Not found"}},
)

@router.get("/challenges", response_model=List[schemas.CTFChallenge])
def read_ctf_challenges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    challenges = crud.get_ctf_challenges(db, skip=skip, limit=limit)
    return challenges

@router.get("/challenges/{challenge_id}", response_model=schemas.CTFChallenge)
def read_ctf_challenge(challenge_id: int, db: Session = Depends(get_db)):
    challenge = crud.get_ctf_challenge(db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="CTF Challenge not found")
    return challenge

@router.get("/scenario/web-basics", response_class=HTMLResponse)
def scenario_web_basics():
    """
    A simple web challenge where the flag is hidden in the source code.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mission: Web Infiltration</title>
        <style>
            body { font-family: 'Courier New', monospace; background: #0d0d0d; color: #00ff00; padding: 2rem; }
            .terminal { border: 1px solid #333; padding: 2rem; max-width: 700px; margin: 0 auto; background: #111; }
            h1 { text-align: center; border-bottom: 1px dashed #333; padding-bottom: 1rem; }
            input { background: #222; border: 1px solid #444; color: #fff; padding: 0.5rem; width: 100%; margin-bottom: 1rem; box-sizing: border-box; }
            button { background: #00ff00; color: #000; border: none; padding: 0.8rem 1.5rem; cursor: pointer; font-weight: bold; width: 100%; }
            button:hover { background: #00cc00; }
            .hint-box { margin-top: 2rem; font-size: 0.8rem; color: #666; }
        </style>
    </head>
    <body>
        <div class="terminal">
            <h1>SECURE LOGIN PORTAL v1.0</h1>
            <p>Access restricted to authorized personnel only.</p>
            <form onsubmit="event.preventDefault(); check();">
                <label>Username</label>
                <input type="text" id="u" placeholder="admin">
                <label>Password</label>
                <input type="password" id="p" placeholder="********">
                <button>AUTHENTICATE</button>
            </form>
            <div id="msg" style="margin-top: 1rem; color: #ff3333;"></div>
            
            <div class="hint-box">
                SYSTEM NOTE: Debug mode enabled. View source enabled.
            </div>
        </div>

        <!-- 
        ========================================
        DEBUG LOG:
        User 'admin' credentials verified.
        Flag: CTF{WEB_BASICS}
        ========================================
        -->

        <script>
            function check() {
                const u = document.getElementById('u').value;
                const p = document.getElementById('p').value;
                // Simple client-side check
                if(u === 'admin' && p === 'password123') {
                    document.getElementById('msg').style.color = '#00ff00';
                    document.getElementById('msg').innerText = 'ACCESS GRANTED. Welcome, Admin.';
                } else {
                    document.getElementById('msg').style.color = '#ff3333';
                    document.getElementById('msg').innerText = 'ACCESS DENIED. Invalid credentials.';
                }
            }
        </script>
    </body>
    </html>
    """

@router.get("/scenario/log-analysis", response_class=HTMLResponse)
def scenario_log_analysis():
    """
    A log analysis challenge presented as a web page table.
    """
    # Generating fake logs
    logs = []
    base_time = 1698300000
    import random
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Googlebot/2.1 (+http://www.google.com/bot.html)"
    ]
    
    paths = ["/login", "/dashboard", "/api/data", "/images/logo.png", "/css/style.css"]
    
    for i in range(50):
        status = 200 if random.random() > 0.2 else 403
        logs.append({
            "timestamp": base_time + i * random.randint(10, 300),
            "ip": f"192.168.1.{random.randint(10, 200)}",
            "method": "GET",
            "path": random.choice(paths),
            "status": status,
            "ua": random.choice(user_agents)
        })
        
    # Insert the flag
    logs.insert(25, {
        "timestamp": base_time + 1500,
        "ip": "10.0.0.1337",
        "method": "POST",
        "path": "/admin/upload?token=CTF{PCAP_ANALYSIS}",
        "status": 200,
        "ua": "MaliciousScript/1.0"
    })
    
    rows = ""
    for log in logs:
        rows += f"<tr><td>{log['timestamp']}</td><td>{log['ip']}</td><td>{log['method']}</td><td>{log['path']}</td><td>{log['status']}</td><td>{log['ua']}</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Server Log Viewer</title>
        <style>
            body {{ font-family: monospace; padding: 20px; background: #f0f0f0; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
            th {{ background: #333; color: white; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            .highlight {{ background: yellow; }}
        </style>
    </head>
    <body>
        <h1>Server Access Logs</h1>
        <p>Suspicious activity reported. Analyze the logs below to find the intruder's token.</p>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>IP Address</th>
                    <th>Method</th>
                    <th>Path</th>
                    <th>Status</th>
                    <th>User Agent</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """

@router.get("/scenario/code-breaker", response_class=HTMLResponse)
def scenario_code_breaker():
    """
    A JavaScript deobfuscation challenge.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>The Vault</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #2c3e50; color: #ecf0f1; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .vault-box { background: #34495e; padding: 3rem; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); text-align: center; }
            input { padding: 10px; font-size: 1.2rem; border-radius: 5px; border: none; margin-top: 1rem; width: 200px; text-align: center; }
            button { padding: 10px 20px; font-size: 1.2rem; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 1rem; }
            button:hover { background: #c0392b; }
        </style>
    </head>
    <body>
        <div class="vault-box">
            <h1>🔒 The Vault</h1>
            <p>Enter the correct PIN to unlock the flag.</p>
            <input type="number" id="pin" placeholder="0000">
            <br>
            <button onclick="unlock()">Unlock</button>
            <p id="result"></p>
        </div>
        
        <script>
            // Obfuscated logic? Not really, just annoying to read.
            var _0x5a1b=['value','getElementById','pin','CTF{RE_EASY}','innerText','Correct! Flag: ','Incorrect PIN'];
            function unlock() {
                var p = document[_0x5a1b[1]](_0x5a1b[2])[_0x5a1b[0]];
                // The secret PIN is 1337 + 420 + 69 = 1826
                if (parseInt(p) === (1337 + 420 + 69)) {
                    document[_0x5a1b[1]]('result')[_0x5a1b[4]] = _0x5a1b[5] + _0x5a1b[3];
                    document[_0x5a1b[1]]('result').style.color = '#2ecc71';
                } else {
                    document[_0x5a1b[1]]('result')[_0x5a1b[4]] = _0x5a1b[6];
                    document[_0x5a1b[1]]('result').style.color = '#e74c3c';
                }
            }
        </script>
    </body>
    </html>
    """

@router.get("/scenario/cookie-monster", response_class=HTMLResponse)
def scenario_cookie_monster():
    """
    A cookie manipulation challenge.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Cookie Monster's Portal</title>
        <style>
            body { font-family: sans-serif; background: #333; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .box { background: #444; padding: 2rem; border-radius: 10px; text-align: center; }
            button { background: #f39c12; border: none; padding: 10px 20px; color: white; cursor: pointer; border-radius: 5px; font-weight: bold; margin-top: 10px; }
            button:hover { background: #d35400; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Admin Panel</h1>
            <p id="msg">Checking access level...</p>
            <p id="flag" style="font-weight: bold; color: #2ecc71;"></p>
            <button onclick="checkAccess()">Check Access</button>
        </div>
        <script>
            // Initialize cookie if not present
            if (!document.cookie.includes('role=')) {
                document.cookie = "role=user; path=/";
            }

            function checkAccess() {
                const cookies = document.cookie.split('; ');
                const roleCookie = cookies.find(row => row.startsWith('role='));
                
                if (roleCookie) {
                    const role = roleCookie.split('=')[1];
                    if (role === 'admin') {
                        document.getElementById('msg').innerText = "Access Granted! Welcome, Admin.";
                        document.getElementById('flag').innerText = "Flag: CTF{COOKIES_ARE_TASTY}";
                    } else {
                        document.getElementById('msg').innerText = "Access Denied. You are currently logged in as '" + role + "'. Only 'admin' can see the flag.";
                    }
                } else {
                    document.getElementById('msg').innerText = "No role cookie found.";
                }
            }
            
            // Auto check on load
            checkAccess();
        </script>
    </body>
    </html>
    """

@router.get("/scenario/sqli-basic", response_class=HTMLResponse)
def scenario_sqli_basic():
    """
    A basic SQL injection challenge (client-side simulation).
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Vulnerable Login</title>
        <style>
            body { font-family: 'Courier New', monospace; background: #000; color: #0f0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-box { border: 2px solid #0f0; padding: 3rem; width: 400px; }
            h2 { text-align: center; margin-top: 0; }
            input { width: 100%; background: #111; border: 1px solid #0f0; color: #0f0; padding: 10px; margin-bottom: 10px; box-sizing: border-box; }
            button { width: 100%; background: #0f0; color: #000; border: none; padding: 10px; font-weight: bold; cursor: pointer; }
            button:hover { background: #0c0; }
            .error { color: red; margin-top: 10px; text-align: center; }
            .success { color: #0f0; margin-top: 10px; text-align: center; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>SYSTEM LOGIN</h2>
            <p>Enter credentials to access the mainframe.</p>
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Password">
            <button onclick="login()">LOGIN</button>
            <div id="message"></div>
        </div>

        <script>
            function login() {
                const user = document.getElementById('username').value;
                const pass = document.getElementById('password').value;
                const msg = document.getElementById('message');

                // Simulate SQL query construction
                // Query: "SELECT * FROM users WHERE username = '" + user + "' AND password = '" + pass + "'"
                
                // Check for basic SQLi pattern
                if (user.includes("' OR '1'='1")) {
                    msg.className = "success";
                    msg.innerHTML = "Query: SELECT * FROM users WHERE username = '' OR '1'='1' ...<br><br>LOGIN SUCCESSFUL!<br>Flag: CTF{SQLI_MASTER}";
                } else if (user === 'admin' && pass === 'supersecret123') {
                     msg.className = "success";
                     msg.innerHTML = "LOGIN SUCCESSFUL!<br>Flag: CTF{SQLI_MASTER}";
                } else {
                    msg.className = "error";
                    msg.innerText = "Access Denied. Invalid credentials.";
                }
            }
        </script>
    </body>
    </html>
    """

@router.get("/status/active", response_model=dict)
def get_active_challenge(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = crud.get_user(db, current_user.id)
    if user.active_challenge_id:
        return {
            "active_challenge_id": user.active_challenge_id,
            "start_time": user.challenge_start_time
        }
    return {"active_challenge_id": None, "start_time": None}

@router.post("/challenges/{challenge_id}/start")
def start_challenge(challenge_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = crud.get_user(db, current_user.id)
    if user.active_challenge_id:
        if user.active_challenge_id == challenge_id:
             return {"message": "Challenge already active", "start_time": user.challenge_start_time}
        raise HTTPException(status_code=400, detail="You already have an active challenge. Finish or end it first.")
    
    challenge = crud.get_ctf_challenge(db, challenge_id=challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    user.active_challenge_id = challenge_id
    user.challenge_start_time = datetime.utcnow()
    db.commit()
    return {"message": "Challenge started", "start_time": user.challenge_start_time}

@router.post("/challenges/end")
def end_challenge(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = crud.get_user(db, current_user.id)
    if not user.active_challenge_id:
         raise HTTPException(status_code=400, detail="No active challenge to end.")
    
    user.active_challenge_id = None
    user.challenge_start_time = None
    db.commit()
    return {"message": "Challenge ended"}

@router.get("/solves/me", response_model=list[int])
def read_my_ctf_solves(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    solves = (
        db.query(models.CTFSolve)
        .filter(models.CTFSolve.user_id == current_user.id)
        .all()
    )
    return [s.challenge_id for s in solves]


@router.post("/report")
def report_ctf_issue(
    report: schemas.CTFReportCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    crud.create_ctf_report(db, report, current_user.id)
    return {"message": "Report submitted"}


@router.post("/challenges/{challenge_id}/submit", response_model=schemas.CTFSubmissionResponse)
def submit_ctf_flag(
    challenge_id: int,
    submission: schemas.CTFSubmission,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    challenge = crud.get_ctf_challenge(db, challenge_id=challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="CTF Challenge not found")

    # Normalize submission
    submitted_flag = submission.flag.strip()
    
    # Try to find standard flag pattern CTF{...} inside the submission
    # This handles "Flag: CTF{...}", "The flag is CTF{...}", etc.
    flag_pattern = re.search(r'ctf\{.*?\}', submitted_flag, re.IGNORECASE)
    if flag_pattern:
        submitted_flag = flag_pattern.group(0)
    else:
        # Fallback for flags that might not follow the standard pattern or if pattern not found
        # Remove common prefixes users might accidentally copy
        if submitted_flag.lower().startswith("flag:"):
            submitted_flag = submitted_flag[5:].strip()
    
    # Case-insensitive comparison
    if submitted_flag.lower() != challenge.flag.strip().lower():
        return schemas.CTFSubmissionResponse(
            message="Incorrect flag.",
            correct=False,
            points_awarded=0,
        )

    user = crud.get_user(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.active_challenge_id != challenge_id:
        raise HTTPException(status_code=400, detail="You must start this challenge before submitting a flag.")

    existing_solve = (
        db.query(models.CTFSolve)
        .filter(
            models.CTFSolve.user_id == user.id,
            models.CTFSolve.challenge_id == challenge.id,
        )
        .first()
    )

    points_awarded = challenge.points

    if existing_solve is None:
        # Clear active challenge upon successful first solve
        user.active_challenge_id = None
        user.challenge_start_time = None
        
        solve = models.CTFSolve(user_id=user.id, challenge_id=challenge.id)
        db.add(solve)

        leaderboard_entry = (
            db.query(models.Leaderboard)
            .filter(models.Leaderboard.user_id == user.id)
            .first()
        )
        if leaderboard_entry:
            leaderboard_entry.points += challenge.points
        else:
            leaderboard_entry = models.Leaderboard(
                user_id=user.id,
                username=user.username,
                points=challenge.points,
            )
            db.add(leaderboard_entry)
    else:
        # Already solved, but we should still clear the active status if it was active
        user.active_challenge_id = None
        user.challenge_start_time = None
        points_awarded = 0

    db.commit()

    total_points = 0
    leaderboard_entry = (
        db.query(models.Leaderboard)
        .filter(models.Leaderboard.user_id == user.id)
        .first()
    )
    if leaderboard_entry:
        total_points = leaderboard_entry.points

    return schemas.CTFSubmissionResponse(
        message="Flag accepted!",
        correct=True,
        points_awarded=points_awarded,
        total_points=total_points,
    )

@router.get("/scenario/hidden-element", response_class=HTMLResponse)
def scenario_hidden_element():
    """
    Challenge: Find the hidden element in the DOM.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hidden in Plain Sight</title>
        <style>
            body { font-family: sans-serif; background: #eee; padding: 2rem; text-align: center; }
            .content { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .secret { display: none; }
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Nothing to see here...</h1>
            <p>Just a regular page with absolutely no secrets.</p>
            <div class="secret" id="flag-container">
                Flag: CTF{HIDDEN_ELEMENTS}
            </div>
        </div>
    </body>
    </html>
    """

@router.get("/scenario/base64-basic", response_class=HTMLResponse)
def scenario_base64_basic():
    """
    Challenge: Decode the Base64 string.
    """
    encoded_flag = "Q1RGe0JBU0U2NF9JU19OT1RfRU5DUllQVElPTn0="
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Base64 Decoder Ring</title>
        <style>
            body {{ font-family: monospace; background: #222; color: #0f0; padding: 2rem; text-align: center; }}
            .code {{ border: 1px dashed #0f0; padding: 1rem; margin: 1rem auto; display: inline-block; font-size: 1.5rem; }}
        </style>
    </head>
    <body>
        <h1>Transmission Received</h1>
        <p>We intercepted this strange string. What does it mean?</p>
        <div class="code">{encoded_flag}</div>
        <p>Hint: It ends with an equals sign.</p>
    </body>
    </html>
    """

@router.get("/scenario/robots", response_class=HTMLResponse)
def scenario_robots():
    """
    Challenge: Check robots.txt.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mr. Robot</title>
        <style>
            body { font-family: sans-serif; background: #333; color: white; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Welcome to the machine.</h1>
        <p>I follow the rules. Do you?</p>
        <p><i>(Hint: Check /ctf/scenario/robots/robots.txt)</i></p>
    </body>
    </html>
    """

@router.get("/scenario/robots/robots.txt")
def scenario_robots_txt():
    from fastapi.responses import PlainTextResponse
    content = "User-agent: *\nDisallow: /secret-flag-location\n\n# Flag: CTF{ROBOTS_RULE}"
    return PlainTextResponse(content)

@router.get("/scenario/header-hunter", response_class=HTMLResponse)
def scenario_header_hunter(response: HTMLResponse):
    """
    Challenge: Find flag in headers.
    """
    # Note: In FastAPI, to set headers on the response we return, we need to use JSONResponse or similar, 
    # but since we are returning HTML directly, we can use the Response object if passed as dependency,
    # or just return a Response object.
    from fastapi.responses import Response
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Head in the Clouds</title>
        <style>
            body { font-family: sans-serif; background: #f0f8ff; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Header Hunter</h1>
        <p>The flag is not in the HTML body. Look higher.</p>
        <p>Open DevTools -> Network -> Reload -> Click the request -> Headers</p>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html", headers={"X-Flag": "CTF{HEADERS_TELL_TALES}"})

@router.get("/scenario/comments", response_class=HTMLResponse)
def scenario_comments():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>No Comment</title>
        <style>
            body { font-family: sans-serif; background: #fff; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Welcome to the Blog</h1>
        <p>There are no posts yet.</p>
        <!-- TODO: Remove this before production. Flag: CTF{COMMENTS_ARE_LEAKY} -->
    </body>
    </html>
    """

@router.get("/scenario/hex-basic", response_class=HTMLResponse)
def scenario_hex_basic():
    hex_string = "4354467b4845585f4348414c4c454e47457d"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hex Decoder</title>
        <style>
            body {{ font-family: monospace; background: #111; color: #0f0; padding: 2rem; text-align: center; }}
            .code {{ border: 1px solid #0f0; padding: 1rem; display: inline-block; margin-top: 1rem; }}
        </style>
    </head>
    <body>
        <h1>Intercepted Transmission</h1>
        <p>The following hex string contains a secret flag.</p>
        <div class="code">{hex_string}</div>
        <p>Can you recover the original text?</p>
    </body>
    </html>
    """

@router.get("/scenario/rot13-basic", response_class=HTMLResponse)
def scenario_rot13_basic():
    encoded = "PGS{EBG13_VF_SHA}"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ROT13 Cipher</title>
        <style>
            body {{ font-family: sans-serif; background: #20232a; color: #61dafb; padding: 2rem; text-align: center; }}
            .cipher {{ font-family: monospace; font-size: 1.5rem; }}
        </style>
    </head>
    <body>
        <h1>Classic Cipher</h1>
        <p>The message below has been encoded.</p>
        <p class="cipher">{encoded}</p>
        <p>Decode it using a simple rotation.</p>
    </body>
    </html>
    """

@router.get("/scenario/xor-basic", response_class=HTMLResponse)
def scenario_xor_basic():
    encoded = "3b 1e 1c 4b 1e 0d 03 4b 06 1e 0d 0d 03 0a"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>XOR Mystery</title>
        <style>
            body {{ font-family: sans-serif; background: #000; color: #0ff; padding: 2rem; text-align: center; }}
            .cipher {{ font-family: monospace; font-size: 1.2rem; }}
        </style>
    </head>
    <body>
        <h1>XOR Mystery</h1>
        <p>An analyst captured this XOR-encoded byte sequence:</p>
        <p class="cipher">{encoded}</p>
        <p>It was encoded with a single-byte key. Can you recover the flag?</p>
    </body>
    </html>
    """

@router.get("/scenario/console-debug", response_class=HTMLResponse)
def scenario_console_debug():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Console Debug</title>
        <style>
            body { font-family: sans-serif; background: #111827; color: #e5e7eb; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Console Debug</h1>
        <p>The application is running in debug mode.</p>
        <p>Developers often log sensitive information during debugging.</p>
        <script>
            console.log("Flag: CTF{CONSOLE_LOG}");
        </script>
    </body>
    </html>
    """

@router.get("/scenario/local-storage", response_class=HTMLResponse)
def scenario_local_storage():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Local Storage Secrets</title>
        <style>
            body { font-family: sans-serif; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Local Storage Secrets</h1>
        <p>This demo app stores configuration data in the browser.</p>
        <p>Some values are not meant to be shown in the UI.</p>
        <script>
            localStorage.setItem('app_theme', 'dark');
            localStorage.setItem('feature_flags', 'beta,ctf');
            localStorage.setItem('secret_flag', 'CTF{LOCAL_STORAGE}');
        </script>
    </body>
    </html>
    """

@router.get("/scenario/layered-encoding", response_class=HTMLResponse)
def scenario_layered_encoding():
    flag = "CTF{LAYERED_ENCODE}"
    rot13_trans = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
    )
    rot13_flag = flag.translate(rot13_trans)
    encoded_bytes = base64.b64encode(rot13_flag.encode("utf-8"))
    encoded = encoded_bytes.decode("utf-8")
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Layered Encoding</title>
        <style>
            body {{ font-family: monospace; background: #0f172a; color: #e5e7eb; padding: 2rem; text-align: center; }}
            .code {{ border: 1px dashed #38bdf8; padding: 1rem; display: inline-block; margin-top: 1rem; }}
        </style>
    </head>
    <body>
        <h1>Layered Encoding</h1>
        <p>The following string hides the flag behind more than one transformation.</p>
        <div class="code">{encoded}</div>
        <p>Peel back each layer until you recover the original text.</p>
    </body>
    </html>
    """

@router.get("/scenario/js-leak", response_class=HTMLResponse)
def scenario_js_leak():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>JS Variable Leak</title>
        <style>
            body { font-family: sans-serif; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>JS Variable Leak</h1>
        <p>This demo app keeps some values only in memory.</p>
        <p>Sometimes developers leave important secrets in variables.</p>
        <script>
            var config = { mode: "demo", version: "1.0.0" };
            var flag = "CTF{JS_LEAK}";
        </script>
    </body>
    </html>
    """

@router.get("/scenario/meta-flag", response_class=HTMLResponse)
def scenario_meta_flag():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Meta Tag Secret</title>
        <meta name="description" content="Demo marketing page.">
        <meta name="environment" content="staging">
        <meta name="flag" content="CTF{META_TAG_SECRET}">
        <style>
            body { font-family: sans-serif; background: #0f172a; color: #e5e7eb; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Meta Tag Secret</h1>
        <p>Metadata about a page is usually stored in the head section.</p>
        <p>Use view-source or DevTools to inspect it.</p>
    </body>
    </html>
    """

@router.get("/scenario/query-debug", response_class=HTMLResponse)
def scenario_query_debug(debug: bool = False):
    if debug:
        body = """
        <h1>Debug Mode Enabled</h1>
        <p>Extra diagnostic information is now visible.</p>
        <pre>flag=CTF{QUERY_DEBUG}</pre>
        """
    else:
        body = """
        <h1>Debug Panel</h1>
        <p>Debug information is currently disabled.</p>
        <p>Try enabling debug mode via the URL parameters.</p>
        """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Query Debug Mode</title>
        <style>
            body {{ font-family: sans-serif; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }}
            pre {{ text-align: left; max-width: 480px; margin: 1rem auto; background: #020617; border: 1px solid #1f2937; padding: 1rem; }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """

@router.get("/scenario/hidden-form", response_class=HTMLResponse)
def scenario_hidden_form():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hidden Form Field</title>
        <style>
            body { font-family: sans-serif; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }
            form { max-width: 360px; margin: 0 auto; }
            input[type="text"] { width: 100%; padding: 8px; margin-bottom: 12px; }
        </style>
    </head>
    <body>
        <h1>Feedback Form</h1>
        <p>Submit your feedback about this demo application.</p>
        <form>
            <input type="text" name="name" placeholder="Name">
            <input type="text" name="feedback" placeholder="Your feedback">
            <input type="hidden" name="flag" value="CTF{HIDDEN_FORM_FIELD}">
            <button type="submit">Submit</button>
        </form>
        <p>The form does not actually submit anywhere.</p>
    </body>
    </html>
    """

@router.get("/scenario/double-base64", response_class=HTMLResponse)
def scenario_double_base64():
    flag = "CTF{DOUBLE_BASE64}"
    once = base64.b64encode(flag.encode("utf-8"))
    twice = base64.b64encode(once)
    encoded = twice.decode("utf-8")
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Double Base64</title>
        <style>
            body {{ font-family: monospace; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }}
            .code {{ border: 1px dashed #22c55e; padding: 1rem; display: inline-block; margin-top: 1rem; }}
        </style>
    </head>
    <body>
        <h1>Double Encoded</h1>
        <p>The string below has been encoded more than once.</p>
        <div class="code">{encoded}</div>
        <p>Decode it step by step until the flag appears.</p>
    </body>
    </html>
    """

@router.get("/scenario/obfus-script", response_class=HTMLResponse)
def scenario_obfus_script():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Obfuscated Script</title>
        <style>
            body { font-family: sans-serif; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }
        </style>
    </head>
    <body>
        <h1>Obfuscated Script</h1>
        <p>The flag is constructed dynamically in JavaScript.</p>
        <p>Read the script and reconstruct it yourself.</p>
        <script>
            const parts = [67, 84, 70, 123, 79, 66, 70, 85, 83, 67, 65, 84, 69, 68, 95, 74, 83, 125];
            const flag = String.fromCharCode.apply(null, parts);
        </script>
    </body>
    </html>
    """

@router.get("/scenario/caesar-shift", response_class=HTMLResponse)
def scenario_caesar_shift():
    encoded = "HWK{FHDVDU_VKLIW}"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Caesar Shift</title>
        <style>
            body {{ font-family: monospace; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Caesar Shift</h1>
        <p>The flag has been shifted by a small, fixed amount.</p>
        <p>{encoded}</p>
        <p>Undo the shift to recover the original text.</p>
    </body>
    </html>
    """

@router.get("/scenario/substitution", response_class=HTMLResponse)
def scenario_substitution():
    cipher = "XUG{ZFKZGXZGXZ_RZKZOB}"
    mapping = "Plain:  ABCDEFGHIJKLMNOPQRSTUVWXYZ\nCipher: QWERTYUIOPASDFGHJKLZXCVBNM"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Substitution Cipher</title>
        <style>
            body {{ font-family: monospace; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }}
            pre {{ text-align: left; max-width: 520px; margin: 1rem auto; }}
        </style>
    </head>
    <body>
        <h1>Substitution Cipher</h1>
        <pre>{mapping}</pre>
        <p>{cipher}</p>
        <p>Use the mapping to convert from cipher text back to plain text.</p>
    </body>
    </html>
    """

@router.get("/scenario/rsa-puzzle", response_class=HTMLResponse)
def scenario_rsa_puzzle():
    n = "25346657"
    e = "17"
    c = "8489080"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>RSA Puzzle</title>
        <style>
            body {{ font-family: monospace; background: #020617; color: #e5e7eb; padding: 2rem; text-align: center; }}
            pre {{ text-align: left; max-width: 520px; margin: 1rem auto; }}
        </style>
    </head>
    <body>
        <h1>RSA Puzzle</h1>
        <pre>n = {n}\ne = {e}\nc = {c}</pre>
        <p>This is a toy RSA example small enough to experiment with.</p>
        <p>Recover the plaintext flag from the ciphertext.</p>
    </body>
    </html>
    """

@router.get("/scenario/log-correlation", response_class=HTMLResponse)
def scenario_log_correlation():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Log Correlation</title>
        <style>
            body { font-family: monospace; background: #020617; color: #e5e7eb; padding: 2rem; }
            pre { background: #020617; border: 1px solid #1f2937; padding: 1rem; margin-bottom: 1rem; }
        </style>
    </head>
    <body>
        <h1>Log Correlation</h1>
        <pre>[auth] id=42 user=analyst action=login status=ok
[pipeline] trace=7f1c job=normalize status=ok
[alerts] corr_id=7f1c severity=low message="benign test event"</pre>
        <pre>[auth] id=77 user=tester action=login status=ok
[pipeline] trace=9ab2 job=decode status=ok
[alerts] corr_id=9ab2 severity=high message="flag=CTF{LOG_CORRELATION}"</pre>
        <p>Match the related lines using their correlation IDs.</p>
    </body>
    </html>
    """

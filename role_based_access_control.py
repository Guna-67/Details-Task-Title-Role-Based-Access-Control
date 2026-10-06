from flask import Flask, request, redirect, render_template_string, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "rbac-demo-secret-key"

# -----------------------------
# Sample users and permissions
# -----------------------------

USERS = {
    "admin": {
        "password": "admin123",
        "role": "Admin"
    },
    "manager": {
        "password": "manager123",
        "role": "Manager"
    },
    "employee": {
        "password": "employee123",
        "role": "Employee"
    }
}

ROLE_PERMISSIONS = {
    "Admin": {
        "view_dashboard",
        "manage_users",
        "manage_roles",
        "view_reports",
        "edit_data",
        "delete_data"
    },
    "Manager": {
        "view_dashboard",
        "view_reports",
        "edit_data"
    },
    "Employee": {
        "view_dashboard"
    }
}

# -----------------------------
# HTML
# -----------------------------

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Role-Based Access Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
        }

        .navbar {
            background: #222;
            color: white;
            padding: 18px 30px;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: 30px auto;
        }

        .card {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            box-shadow: 0 3px 10px #ccc;
        }

        input {
            width: 100%;
            padding: 11px;
            margin: 8px 0 15px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        button, .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            color: white;
            background: #007bff;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }

        .logout {
            background: #dc3545;
        }

        .success {
            background: #d4edda;
            padding: 12px;
            border-radius: 6px;
        }

        .danger {
            background: #f8d7da;
            padding: 12px;
            border-radius: 6px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }

        .permission {
            display: inline-block;
            background: #e9ecef;
            padding: 6px 10px;
            margin: 4px;
            border-radius: 15px;
        }
    </style>
</head>

<body>

{% if session.get("username") %}
<div class="navbar">
    <b>RBAC System</b>
    &nbsp; | &nbsp;
    Logged in as: {{ session["username"] }}
    &nbsp; | &nbsp;
    Role: {{ session["role"] }}
</div>
{% endif %}

<div class="container">

    {% if message %}
        <div class="{{ message_type }}">
            {{ message }}
        </div>
    {% endif %}

    {% if page == "login" %}

        <div class="card">
            <h1>🔐 Role-Based Access Control</h1>
            <p>Login using one of the demo accounts.</p>

            <form method="POST" action="/login">

                <label>Username</label>
                <input type="text" name="username" required>

                <label>Password</label>
                <input type="password" name="password" required>

                <button type="submit">Login</button>

            </form>

            <hr>

            <p><b>Demo accounts:</b></p>
            <p>Admin: admin / admin123</p>
            <p>Manager: manager / manager123</p>
            <p>Employee: employee / employee123</p>
        </div>

    {% else %}

        <div class="card">

            <h1>Dashboard</h1>

            <p>
                Welcome <b>{{ session["username"] }}</b>.
            </p>

            <p>
                Your role:
                <b>{{ session["role"] }}</b>
            </p>

            <a class="btn logout" href="/logout">Logout</a>

        </div>

        <div class="card">

            <h2>🔑 Your Permissions</h2>

            {% for permission in permissions %}
                <span class="permission">{{ permission }}</span>
            {% endfor %}

        </div>

        {% if "manage_users" in permissions %}

        <div class="card">

            <h2>👥 User Management</h2>

            <table>
                <tr>
                    <th>Username</th>
                    <th>Role</th>
                </tr>

                {% for username, user in users.items() %}
                <tr>
                    <td>{{ username }}</td>
                    <td>{{ user["role"] }}</td>
                </tr>
                {% endfor %}

            </table>

        </div>

        {% endif %}

        {% if "view_reports" in permissions %}

        <div class="card">

            <h2>📊 Reports</h2>

            <p>
                You have permission to view system reports.
            </p>

            <button onclick="alert('Sample report opened!')">
                View Report
            </button>

        </div>

        {% endif %}

        {% if "edit_data" in permissions %}

        <div class="card">

            <h2>✏️ Data Management</h2>

            <p>
                You have permission to edit system data.
            </p>

            <button onclick="alert('Edit access granted!')">
                Edit Data
            </button>

        </div>

        {% endif %}

        {% if "delete_data" in permissions %}

        <div class="card">

            <h2>🗑️ Delete Access</h2>

            <p>
                You have permission to delete data.
            </p>

            <button onclick="alert('Delete access granted!')">
                Delete Data
            </button>

        </div>

        {% endif %}

        <div class="card">

            <h2>🛡️ Role Permissions</h2>

            <table>

                <tr>
                    <th>Role</th>
                    <th>Permissions</th>
                </tr>

                {% for role, role_permissions in role_permissions.items() %}

                <tr>
                    <td><b>{{ role }}</b></td>

                    <td>
                        {% for permission in role_permissions %}
                            <span class="permission">
                                {{ permission }}
                            </span>
                        {% endfor %}
                    </td>
                </tr>

                {% endfor %}

            </table>

        </div>

    {% endif %}

</div>

</body>
</html>
"""

# -----------------------------
# Helper functions
# -----------------------------

def render_page(message=None, message_type="success"):
    if "username" not in session:
        return render_template_string(
            HTML,
            page="login",
            message=message,
            message_type=message_type,
            permissions=[],
            users=USERS,
            role_permissions=ROLE_PERMISSIONS
        )

    role = session["role"]
    permissions = ROLE_PERMISSIONS.get(role, set())

    return render_template_string(
        HTML,
        page="dashboard",
        message=message,
        message_type=message_type,
        permissions=permissions,
        users=USERS,
        role_permissions=ROLE_PERMISSIONS
    )


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):

            if "username" not in session:
                return redirect("/")

            role = session["role"]

            if permission not in ROLE_PERMISSIONS.get(role, set()):
                return render_page(
                    "Access denied. You do not have this permission.",
                    "danger"
                )

            return function(*args, **kwargs)

        return wrapper

    return decorator


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    if "username" in session:
        return render_page()

    return render_page()


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = USERS.get(username)

    if user and user["password"] == password:

        session["username"] = username
        session["role"] = user["role"]

        return redirect("/")

    return render_page(
        "Invalid username or password.",
        "danger"
    )


@app.route("/logout")
def logout():

    session.clear()

    return render_page(
        "Logged out successfully.",
        "success"
    )


@app.route("/admin")
@permission_required("manage_users")
def admin():

    return render_page("Admin access granted!")


if __name__ == "__main__":

    print("=" * 55)
    print("ROLE-BASED ACCESS CONTROL SYSTEM")
    print("=" * 55)
    print("Open: http://127.0.0.1:5000")
    print()
    print("Demo login:")
    print("Admin    -> admin / admin123")
    print("Manager  -> manager / manager123")
    print("Employee -> employee / employee123")
    print("=" * 55)

    app.run(debug=True)

#!/usr/bin/env python3
import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route handling
        if self.path == '/':
            self.serve_file('index.html')
        elif self.path == '/signup':
            self.serve_file('Admin Panel/index.html')
        elif self.path == '/dashboard':
            self.serve_file('dashboard.html')
        elif self.path == '/signin':
            self.serve_file('sign in page/signin.html')
        elif self.path == '/about':
            self.serve_file('about.html')
        elif self.path == '/services':
            self.serve_file('services.html')
        elif self.path == '/contact':
            self.serve_file('contact.html')
        else:
            super().do_GET()

    def serve_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "File not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def do_GET_original(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expense Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            width: 400px;
            max-width: 90%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="email"], input[type="password"], input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="email"]:focus, input[type="password"]:focus, input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .links {
            text-align: center;
            margin-top: 20px;
        }
        .links a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Expense Management System</h1>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="Enter your email">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter your password">
            </div>
            
            <button type="submit">Sign In</button>
            
            <div id="successMsg" class="success" style="display: none;">
                ✅ Login Successful! Welcome to the Expense Management System
            </div>
        </form>
        
        <div class="links">
            <a href="#" onclick="showSignup()">Sign Up</a>
            <a href="#" onclick="showForgotPassword()">Forgot Password?</a>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (email && password) {
                document.getElementById('successMsg').style.display = 'block';
                setTimeout(() => {
                    alert('🎉 Welcome to the Expense Management System!\\n\\nFeatures Available:\\n• User Management\\n• Expense Tracking\\n• Approval Workflows\\n• Admin Dashboard\\n\\nThis is a demo version running on a simple HTTP server.');
                }, 500);
            }
        });

        function showSignup() {
            alert('📝 Sign Up Feature\\n\\nTo create an account:\\n1. Contact your administrator\\n2. Or use the admin panel\\n\\nThis demo shows the login interface.');
        }

        function showForgotPassword() {
            alert('🔐 Password Reset\\n\\nTo reset your password:\\n1. Contact your administrator\\n2. Or use the password reset API\\n\\nThis demo shows the login interface.');
        }
    </script>
</body>
</html>
            """
            self.wfile.write(html_content.encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'status': 'success', 'message': 'Login successful!'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/auth/signup':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {'status': 'success', 'message': 'Registration successful!', 'access_token': 'demo_token_123'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    PORT = 5000
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print("📱 Open your browser and go to http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        httpd.serve_forever()

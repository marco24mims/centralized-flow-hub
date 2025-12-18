import React from 'react';
import './LoginPrompt.css';

const LoginPrompt = ({ authError }) => {
  const handleLogin = (system) => {
    const urls = {
      laravel11: 'http://localhost/v2/login',
      laravel9: 'http://localhost/login'
    };
    window.location.href = urls[system];
  };

  return (
    <div className="login-prompt-container">
      <div className="login-prompt-card">
        <div className="login-prompt-header">
          <svg className="login-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <h2>Authentication Required</h2>
        </div>

        <p className="login-prompt-message">
          Please login to access CFH Project Management System
        </p>

        {authError && (
          <div className="auth-error">
            {authError}
          </div>
        )}

        <div className="login-buttons">
          <button
            className="login-button laravel11"
            onClick={() => handleLogin('laravel11')}
          >
            <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Login to Banner System (V2)
          </button>

          <button
            className="login-button laravel9"
            onClick={() => handleLogin('laravel9')}
          >
            <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Login to Digital Operations
          </button>
        </div>

        <div className="login-footer">
          <p>After logging in, you'll be redirected back to CFH Project Management</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPrompt;

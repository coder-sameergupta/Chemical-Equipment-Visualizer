import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useTheme } from '../context/ThemeContext';

const Login = ({ setAuth }) => {
    const { theme, toggleTheme } = useTheme();
    const [isLogin, setIsLogin] = useState(true);
    const [showForgotPassword, setShowForgotPassword] = useState(false);

    // Form States
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');

    // UI States
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await api.post('login/', { username, password });
            localStorage.setItem('token', res.data.token);
            setAuth(true);
            navigate('/');
        } catch (err) {
            console.error(err);
            setError('Invalid username or password');
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.post('register/', { username, email, password });
            setMessage('Registration successful! Please log in.');
            setIsLogin(true);
            setUsername('');
            setPassword('');
        } catch (err) {
            console.error(err);
            if (err.response && err.response.data) {
                // Flatten error messages
                const errorMsg = Object.values(err.response.data).flat().join(' ');
                setError(errorMsg || 'Registration failed.');
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);

        try {
            await api.post('password-reset/', { email });
            setMessage('Password reset link has been sent to your email (check console).');
            // Don't close the form immediately so user can read the message
        } catch (err) {
            console.error(err);
            setError('Failed to send reset link. Check your email address.');
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setError('');
        setMessage('');
        setIsLogin(!isLogin);
        setShowForgotPassword(false);
    };

    return (
        <div className="grid-background" style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            color: 'var(--text-primary)',
            transition: 'background 0.3s ease'
        }}>
            {/* Generating random floating particles */}
            {[...Array(20)].map((_, i) => (
                <div
                    key={i}
                    className="floating-particle"
                    style={{
                        width: `${Math.random() * 6 + 2}px`,
                        height: `${Math.random() * 6 + 2}px`,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        animationDelay: `${Math.random() * 5}s`,
                        animationDuration: `${Math.random() * 10 + 5}s`
                    }}
                />
            ))}

            <button
                onClick={toggleTheme}
                style={{
                    position: 'absolute',
                    top: '20px',
                    right: '20px',
                    padding: '10px',
                    borderRadius: '50%',
                    border: '1px solid var(--glass-border)',
                    background: 'var(--glass-bg)',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    width: '40px',
                    height: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
                title="Toggle Theme"
            >
                {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            <div className="glass-card" style={{ width: '400px', padding: '3rem' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2rem', fontWeight: 700 }}>
                    {showForgotPassword ? 'Reset Password' : (isLogin ? 'Sign In' : 'Sign Up')}
                </h2>

                {message && (
                    <div style={{
                        background: 'rgba(16, 185, 129, 0.2)',
                        color: 'var(--success)',
                        padding: '10px',
                        borderRadius: '8px',
                        marginBottom: '1rem',
                        textAlign: 'center',
                        fontSize: '0.9rem'
                    }}>
                        {message}
                    </div>
                )}

                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.2)',
                        color: 'var(--danger)',
                        padding: '10px',
                        borderRadius: '8px',
                        marginBottom: '1rem',
                        textAlign: 'center',
                        fontSize: '0.9rem'
                    }}>
                        {error}
                    </div>
                )}

                {showForgotPassword ? (
                    <form onSubmit={handleForgotPassword}>
                        <div style={{ marginBottom: '2rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="e.g. user@example.com"
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '12px',
                                    background: 'var(--input-bg)',
                                    border: '1px solid var(--input-border)',
                                    color: 'var(--text-primary)',
                                    outline: 'none',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>
                        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', padding: '14px', marginBottom: '1rem' }}>
                            {loading ? 'Sending...' : 'Send Reset Link'}
                        </button>
                        <div style={{ textAlign: 'center' }}>
                            <span
                                onClick={() => setShowForgotPassword(false)}
                                style={{ color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.9rem' }}
                            >
                                Back to Sign In
                            </span>
                        </div>
                    </form>
                ) : (
                    <form onSubmit={isLogin ? handleLogin : handleRegister}>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="e.g. admin"
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '12px',
                                    background: 'var(--input-bg)',
                                    border: '1px solid var(--input-border)',
                                    color: 'var(--text-primary)',
                                    outline: 'none',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>

                        {!isLogin && (
                            <div style={{ marginBottom: '1.5rem' }}>
                                <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Email</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="e.g. user@example.com"
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        borderRadius: '12px',
                                        background: 'var(--input-bg)',
                                        border: '1px solid var(--input-border)',
                                        color: 'var(--text-primary)',
                                        outline: 'none',
                                        fontSize: '1rem'
                                    }}
                                />
                            </div>
                        )}

                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="e.g. password123"
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '12px',
                                    background: 'var(--input-bg)',
                                    border: '1px solid var(--input-border)',
                                    color: 'var(--text-primary)',
                                    outline: 'none',
                                    fontSize: '1rem'
                                }}
                            />
                        </div>

                        {isLogin && (
                            <div style={{ marginBottom: '2rem', textAlign: 'right' }}>
                                <span
                                    onClick={() => setShowForgotPassword(true)}
                                    style={{ color: 'var(--accent)', cursor: 'pointer', fontSize: '0.9rem' }}
                                >
                                    Forgot Password?
                                </span>
                            </div>
                        )}

                        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', padding: '14px', marginBottom: '1.5rem' }}>
                            {loading ? (isLogin ? 'Signing In...' : 'Registering...') : (isLogin ? 'Access Dashboard' : 'Create Account')}
                        </button>

                        <div style={{ textAlign: 'center' }}>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                {isLogin ? "Don't have an account? " : "Already have an account? "}
                            </span>
                            <span
                                onClick={toggleMode}
                                style={{ color: 'var(--accent)', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem' }}
                            >
                                {isLogin ? 'Sign Up' : 'Sign In'}
                            </span>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default Login;

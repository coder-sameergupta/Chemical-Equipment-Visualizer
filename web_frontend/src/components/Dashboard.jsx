import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useTheme } from '../context/ThemeContext';
import { Line, Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Outfit' } } },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: '#f8fafc',
            bodyColor: '#cbd5e1',
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
        }
    },
    scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
    }
};

const Dashboard = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [history, setHistory] = useState([]);
    const [currentUpload, setCurrentUpload] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    const { theme, toggleTheme } = useTheme();

    useEffect(() => {
        fetchHistory();
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const res = await api.get('profile/');
            setUser(res.data);
        } catch (err) {
            console.error("Failed to fetch profile", err);
        }
    };

    const fetchHistory = async () => {
        try {
            const res = await api.get('history/');
            setHistory(res.data);
            if (res.data.length > 0 && !currentUpload && activeTab === 'dashboard') {
                // Optionally auto-load first, but kept manual for now
            }
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
        window.location.reload();
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        try {
            const res = await api.post('upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            await fetchHistory();
            await loadDashboard(res.data.id);
            setActiveTab('dashboard');
        } catch (err) {
            console.error(err);
            alert(`Upload failed: ${err.response?.data?.error || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const loadDashboard = async (id) => {
        setLoading(true);
        try {
            const [summaryRes, dataRes] = await Promise.all([
                api.get(`summary/${id}/`),
                api.get(`data/${id}/`)
            ]);
            setStats(summaryRes.data);
            setCurrentUpload({ id, data: dataRes.data });
            setActiveTab('dashboard');
        } catch (err) {
            console.error(err);
            alert("Failed to load data for this upload.");
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await api.get('users/');
            setUsers(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        if (activeTab === 'users') {
            fetchUsers();
        }
    }, [activeTab]);

    const handleDownloadReport = async (uploadId) => {
        try {
            const res = await api.get(`report/${uploadId}/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${uploadId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Failed to download report", err);
            alert("Failed to download report.");
        }
    };

    const getChartData = () => {
        if (!currentUpload || !stats) return null;
        const labels = currentUpload.data.map(d => d.equipment_name);
        return {
            parameters: {
                labels,
                datasets: [
                    {
                        label: 'Flow (L/min)',
                        data: currentUpload.data.map(d => d.flowrate),
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                    },
                    {
                        label: 'Press (bar)',
                        data: currentUpload.data.map(d => d.pressure),
                        borderColor: '#f87171',
                        backgroundColor: 'rgba(248, 113, 113, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                    }
                ]
            },
            distribution: {
                labels: stats.type_distribution.map(d => d.equipment_type),
                datasets: [{
                    label: 'Count',
                    data: stats.type_distribution.map(d => d.count),
                    backgroundColor: ['#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fbbf24'],
                    borderRadius: 8,
                }]
            }
        };
    };

    const charts = getChartData();

    return (
        <div className="app-container">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="sidebar-brand">ChemVisualizer</div>

                <div className="section-label">Menu</div>
                <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
                    <span>📊 Dashboard</span>
                </div>
                <div className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
                    <span>📜 History</span>
                </div>
                <div className={`nav-item ${activeTab === 'upload' ? 'active' : ''}`} onClick={() => setActiveTab('upload')}>
                    <span>📤 Upload CSV</span>
                </div>
                <div className={`nav-item ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
                    <span>👥 Users</span>
                </div>

                <div className="nav-item" onClick={toggleTheme}>
                    <span>{theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}</span>
                </div>

                <div className="nav-item" onClick={handleLogout} style={{ marginTop: 'auto', color: 'var(--danger)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                    <span>🚪 Logout</span>
                </div>
            </div>

            {/* Main Content */}
            <div className="main-content">

                {/* --- TAB: DASHBOARD --- */}
                {activeTab === 'dashboard' && (
                    <div className="animate-fade-in">
                        {!stats ? (
                            <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
                                <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
                                    {user ? `Welcome, ${user.username}` : 'Dashboard'}
                                </h2>
                                <p style={{ color: 'var(--text-secondary)' }}>
                                    Select an upload from the <b>History</b> tab or upload new data.
                                </p>
                            </div>
                        ) : (
                            <>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                                    <div>
                                        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>
                                            {user ? `Welcome, ${user.username}` : 'Analytics Overview'}
                                        </h1>
                                        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Viewing Upload #{currentUpload.id}</p>
                                    </div>
                                    <button
                                        onClick={() => handleDownloadReport(currentUpload.id)}
                                        className="btn-primary"
                                        style={{ textDecoration: 'none' }}
                                    >
                                        Download Report
                                    </button>
                                </div>
                                <div className="stats-grid">
                                    <div className="glass-card stat-card"><span className="stat-label">Total Equipment</span><span className="stat-value">{stats.total_count}</span></div>
                                    <div className="glass-card stat-card"><span className="stat-label">Avg Flow</span><span className="stat-value">{stats.averages.avg_flowrate?.toFixed(2)}</span></div>
                                    <div className="glass-card stat-card"><span className="stat-label">Avg Press</span><span className="stat-value">{stats.averages.avg_pressure?.toFixed(2)}</span></div>
                                    <div className="glass-card stat-card"><span className="stat-label">Avg Temp</span><span className="stat-value">{stats.averages.avg_temperature?.toFixed(2)}</span></div>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
                                    <div className="glass-card"><div className="card-title">Parameter Trends</div><div className="chart-container"><Line data={charts.parameters} options={chartOptions} /></div></div>
                                    <div className="glass-card"><div className="card-title">Type Distribution</div><div className="chart-container"><Bar data={charts.distribution} options={chartOptions} /></div></div>
                                </div>
                                <div className="glass-card">
                                    <div className="card-title">Raw Data</div>
                                    <div className="table-container">
                                        <table className="custom-table">
                                            <thead>
                                                <tr><th>Equipment Name</th><th>Type</th><th>Flowrate</th><th>Pressure</th><th>Temp</th></tr>
                                            </thead>
                                            <tbody>
                                                {currentUpload.data.map(row => (
                                                    <tr key={row.id}>
                                                        <td style={{ fontWeight: 500, color: 'var(--accent)' }}>{row.equipment_name}</td>
                                                        <td>{row.equipment_type}</td>
                                                        <td>{row.flowrate}</td>
                                                        <td>{row.pressure}</td>
                                                        <td>{row.temperature}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* --- TAB: HISTORY --- */}
                {activeTab === 'history' && (
                    <div className="animate-fade-in">
                        <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Upload History</h2>
                        <div className="glass-card">
                            <table className="custom-table">
                                <thead>
                                    <tr><th>ID</th><th>Uploaded By</th><th>Date</th><th>Filename</th><th>Records</th><th>Actions</th></tr>
                                </thead>
                                <tbody>
                                    {history.map(item => (
                                        <tr key={item.id}>
                                            <td>#{item.id}</td>
                                            <td style={{ fontWeight: 600, color: 'var(--accent)' }}>{item.user || 'Unknown'}</td>
                                            <td>{new Date(item.uploaded_at).toLocaleString()}</td>
                                            <td>{item.file.split('/').pop()}</td>
                                            <td>{item.total_records}</td>
                                            <td>
                                                <button
                                                    className="btn-primary"
                                                    style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                                                    onClick={() => loadDashboard(item.id)}
                                                >
                                                    View
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* --- TAB: UPLOAD --- */}
                {activeTab === 'upload' && (
                    <div className="animate-fade-in glass-card" style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center', padding: '3rem' }}>
                        <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Upload Data</h2>
                        <label className="upload-zone" style={{ display: 'block', padding: '4rem' }}>
                            <input type="file" accept=".csv" hidden onChange={handleFileUpload} />
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>☁️</div>
                            <div style={{ fontWeight: 600, fontSize: '1.2rem', color: 'var(--accent)' }}>
                                {loading ? 'Processing...' : 'Click to Select CSV File'}
                            </div>
                        </label>
                    </div>
                )}

                {/* --- TAB: USERS --- */}
                {activeTab === 'users' && (
                    <div className="animate-fade-in">
                        <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Registered Users</h2>
                        <div className="glass-card">
                            <table className="custom-table">
                                <thead>
                                    <tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th></tr>
                                </thead>
                                <tbody>
                                    {users.map(user => (
                                        <tr key={user.id}>
                                            <td>#{user.id}</td>
                                            <td style={{ fontWeight: 600, color: 'white' }}>{user.username}</td>
                                            <td>{user.email || 'N/A'}</td>
                                            <td>
                                                <span style={{
                                                    background: user.is_staff ? 'rgba(56, 189, 248, 0.2)' : 'rgba(148, 163, 184, 0.2)',
                                                    color: user.is_staff ? '#38bdf8' : '#94a3b8',
                                                    padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem'
                                                }}>
                                                    {user.is_staff ? 'Admin' : 'User'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;

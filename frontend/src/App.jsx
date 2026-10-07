import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomeFeed from './pages/HomeFeed';
import ItemDetail from './pages/ItemDetail';
import ProfilePage from './pages/ProfilePage';
import ChatRoom from './pages/ChatRoom';
import CreateListing from './pages/CreateListing';
import MyRentals from './pages/MyRentals';
import LoginModal from './pages/LoginModal';
import FeedbackPage from './pages/FeedbackPage';
import { api } from './services/api';
import { Link } from 'react-router-dom';

export default function App() {
  const [user, setUser] = useState(null);
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  useEffect(() => {
    // Check local storage on mount
    const savedUser = localStorage.getItem('hostelshare_user');
    const token = localStorage.getItem('hostelshare_token');
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
        // Verify with server
        api.getMe().then((res) => {
          setUser(res.data);
          localStorage.setItem('hostelshare_user', JSON.stringify(res.data));
        }).catch(() => {
          // Token invalid or expired
        });
      } catch (e) {
        localStorage.removeItem('hostelshare_user');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('hostelshare_token');
    localStorage.removeItem('hostelshare_user');
    setUser(null);
  };

  const handleAuthSuccess = (updatedUser) => {
    setUser(updatedUser);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-canvas text-zinc-900 selection:bg-lime-200 selection:text-zinc-950">
        
        {/* Navigation Bar */}
        <Navbar
          user={user}
          onOpenLogin={() => setLoginModalOpen(true)}
          onLogout={handleLogout}
        />

        {/* Route Pages */}
        <main className="flex-1 pb-16">
          <Routes>
            <Route path="/" element={<HomeFeed onOpenLogin={() => setLoginModalOpen(true)} user={user} />} />
            <Route path="/items/:id" element={<ItemDetail user={user} onOpenLogin={() => setLoginModalOpen(true)} />} />
            <Route path="/u/:username" element={<ProfilePage currentUser={user} />} />
            <Route path="/profile" element={<ProfilePage currentUser={user} />} />
            <Route path="/rentals" element={<MyRentals user={user} onOpenLogin={() => setLoginModalOpen(true)} />} />
            <Route path="/chat/:rentalId" element={<ChatRoom currentUser={user} />} />
            <Route path="/create-listing" element={<CreateListing user={user} onOpenLogin={() => setLoginModalOpen(true)} />} />
            <Route path="/feedback" element={<FeedbackPage user={user} onOpenLogin={() => setLoginModalOpen(true)} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Global Footer - Gen-Z Minimal */}
        <footer className="border-t border-zinc-200 bg-white py-8 text-center text-xs text-zinc-500 space-y-2.5 font-mono">
          <p className="font-semibold text-zinc-700">HostelShare — Campus Peer-to-Peer Rental & Utility Sharing Service</p>
          <div className="flex items-center justify-center gap-4 text-xs font-sans">
            <Link to="/feedback" className="font-bold text-zinc-900 hover:text-lime-600 underline underline-offset-4 decoration-lime-400 transition-colors">
              Platform & Faculty Feedback Form
            </Link>
            <span className="text-zinc-300">•</span>
            <Link to="/" className="text-zinc-600 hover:text-zinc-950 transition-colors">
              Browse Utilities
            </Link>
          </div>
          <p className="text-[11px] text-zinc-400">
            Protected by Mutual Privacy Shield — Dual-Handshake Physical Verification Protocol
          </p>
        </footer>


        {/* Global Login & Onboarding Modal */}
        <LoginModal
          isOpen={loginModalOpen}
          onClose={() => setLoginModalOpen(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      </div>
    </BrowserRouter>
  );
}

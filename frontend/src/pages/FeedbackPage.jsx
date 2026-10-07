import React, { useState, useEffect } from 'react';
import { 
  Star, 
  MessageSquare, 
  CheckCircle2, 
  Award, 
  ShieldCheck, 
  Sparkles, 
  Send, 
  BarChart3, 
  Filter, 
  Clock, 
  UserCheck, 
  ThumbsUp, 
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';

const CATEGORIES = [
  { id: 'Overall Experience', label: 'Overall Experience', desc: 'General feel & satisfaction' },
  { id: 'Hostel & Handshake Flow', label: 'PIN Handshake & Security', desc: 'Physical verification protocol' },
  { id: 'UI/UX & Design', label: 'UI / UX Design', desc: 'Visual clarity & ease of use' },
  { id: 'Feature Suggestion', label: 'Feature Suggestion', desc: 'Ideas for future sprints' },
  { id: 'Bug Report', label: 'Bug / Issue', desc: 'Found an edge case or glitch' },
  { id: 'Academic & Faculty Evaluation', label: 'Faculty / Project Evaluation', desc: 'Formal curriculum evaluation' }
];

const ROLES = [
  'Hostel Student',
  'Faculty Evaluator',
  'Peer Reviewer',
  'Guest / Visitor'
];

const RECOMMEND_OPTIONS = [
  { value: 'Definitely', label: 'Definitely', sub: 'Must-have on campus' },
  { value: 'Likely', label: 'Likely', sub: 'Very useful utility' },
  { value: 'Neutral', label: 'Neutral', sub: 'Could be helpful' },
  { value: 'Unlikely', label: 'Unlikely', sub: 'Needs major overhaul' }
];

export default function FeedbackPage({ user, onOpenLogin }) {
  const [activeTab, setActiveTab] = useState('form'); // 'form' | 'feed'
  
  // Form State
  const [formData, setFormData] = useState({
    name: user?.display_name || '',
    email: '',
    role: 'Hostel Student',
    category: 'Overall Experience',
    overall_rating: 5,
    ease_of_use: 5,
    trust_safety: 5,
    recommend: 'Definitely',
    feedback_text: ''
  });

  const [hoverRating, setHoverRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formError, setFormError] = useState(null);

  // Feed & Stats State
  const [stats, setStats] = useState(null);
  const [feedbacks, setFeedbacks] = useState([]);
  const [feedLoading, setFeedLoading] = useState(false);
  const [feedCategory, setFeedCategory] = useState('All');

  // Pre-fill user data when user changes
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        name: prev.name || user.display_name || `@${user.username}`
      }));
    }
  }, [user]);

  // Load stats and feedbacks on mount
  const loadStatsAndFeed = async () => {
    try {
      setFeedLoading(true);
      const [statsRes, listRes] = await Promise.all([
        api.getFeedbackStats().catch(() => ({ data: null })),
        api.getFeedbacks({ category: feedCategory === 'All' ? undefined : feedCategory }).catch(() => ({ data: [] }))
      ]);
      if (statsRes?.data) setStats(statsRes.data);
      if (listRes?.data) setFeedbacks(listRes.data);
    } catch (err) {
      console.error('Failed to load feedback data:', err);
    } finally {
      setFeedLoading(false);
    }
  };

  useEffect(() => {
    loadStatsAndFeed();
  }, [feedCategory]);

  const handleRatingClick = (field, val) => {
    setFormData(prev => ({ ...prev, [field]: val }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.feedback_text.trim() || formData.feedback_text.trim().length < 5) {
      setFormError('Please enter at least 5 characters sharing your feedback or remarks.');
      return;
    }

    try {
      setSubmitting(true);
      await api.submitFeedback({
        ...formData,
        feedback_text: formData.feedback_text.trim()
      });
      setSubmitted(true);
      // Reload stats in background
      loadStatsAndFeed();
    } catch (err) {
      console.error(err);
      setFormError(err.response?.data?.detail || 'Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleResetForm = () => {
    setSubmitted(false);
    setFormData({
      name: user?.display_name || '',
      email: '',
      role: 'Hostel Student',
      category: 'Overall Experience',
      overall_rating: 5,
      ease_of_use: 5,
      trust_safety: 5,
      recommend: 'Definitely',
      feedback_text: ''
    });
  };

  const getRatingLabel = (score) => {
    switch (score) {
      case 5: return 'Outstanding — Seamless Experience';
      case 4: return 'Very Good — Smooth & Useful';
      case 3: return 'Decent — Functional, minor friction';
      case 2: return 'Needs Work — Rough edges found';
      case 1: return 'Poor — Encountered issues';
      default: return '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header Banner - Gen-Z Minimal */}
      <div className="rounded-2xl p-6 sm:p-8 border border-zinc-200 bg-white shadow-2xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-lime-100 text-lime-900 border border-lime-300 text-[10px] font-mono uppercase font-bold tracking-widest">
            <Sparkles className="w-3 h-3 text-lime-600" />
            <span>Project & Academic Evaluation</span>
          </div>
          
          <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-500">
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-700" />
            <span>Faculty Mandated Survey</span>
          </div>
        </div>

        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-zinc-950">
            Platform & Campus Feedback Form
          </h1>
          <p className="mt-1.5 text-xs sm:text-sm text-zinc-600 leading-relaxed max-w-2xl">
            As mandated for university project evaluation, your feedback directly shapes the development and grading of HostelShare. Please share your hands-on experience, usability review, or feature suggestions.
          </p>
        </div>

        {/* Real-time Community & Faculty Stats Snapshot */}
        {stats && stats.total_feedbacks > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-zinc-100">
            <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Average Score</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <Star className="w-4 h-4 fill-amber-400 text-amber-500" />
                <span className="text-lg font-black text-zinc-950 font-mono">{stats.average_rating.toFixed(1)}</span>
                <span className="text-xs text-zinc-400 font-mono">/ 5.0</span>
              </div>
            </div>

            <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Total Submissions</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <MessageSquare className="w-4 h-4 text-zinc-700" />
                <span className="text-lg font-black text-zinc-950 font-mono">{stats.total_feedbacks}</span>
                <span className="text-xs text-zinc-500 font-medium">reviews</span>
              </div>
            </div>

            <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Ease of Use</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <ThumbsUp className="w-4 h-4 text-lime-600" />
                <span className="text-lg font-black text-zinc-950 font-mono">{stats.average_ease_of_use.toFixed(1)}</span>
                <span className="text-xs text-zinc-400 font-mono">/ 5.0</span>
              </div>
            </div>

            <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Trust & Privacy</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <ShieldCheck className="w-4 h-4 text-zinc-900" />
                <span className="text-lg font-black text-zinc-950 font-mono">{stats.average_trust_safety.toFixed(1)}</span>
                <span className="text-xs text-zinc-400 font-mono">/ 5.0</span>
              </div>
            </div>
          </div>
        )}

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-2 pt-2">
          <button
            type="button"
            onClick={() => setActiveTab('form')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'form'
                ? 'bg-zinc-950 text-white shadow-xs'
                : 'bg-zinc-100 text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/70'
            }`}
          >
            Submit Feedback
          </button>
          
          <button
            type="button"
            onClick={() => setActiveTab('feed')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'feed'
                ? 'bg-zinc-950 text-white shadow-xs'
                : 'bg-zinc-100 text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200/70'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Faculty & Peer Reviews ({feedbacks.length})</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === 'form' ? (
        submitted ? (
          /* Submission Celebration Card */
          <div className="rounded-2xl p-8 sm:p-12 border border-zinc-200 bg-white text-center space-y-6">
            <div className="w-16 h-16 bg-lime-100 text-lime-700 border border-lime-300 rounded-2xl mx-auto flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 stroke-[2.5]" />
            </div>

            <div className="space-y-2 max-w-md mx-auto">
              <h2 className="text-xl sm:text-2xl font-black text-zinc-950">
                Feedback Recorded Successfully
              </h2>
              <p className="text-xs sm:text-sm text-zinc-600 leading-relaxed">
                Thank you for contributing to the academic evaluation and improvement of HostelShare. Your rating and remarks have been logged for faculty review.
              </p>
            </div>

            <div className="p-4 bg-zinc-50 rounded-xl border border-zinc-200 max-w-md mx-auto text-left space-y-2 text-xs">
              <div className="flex justify-between items-center text-zinc-500 font-mono">
                <span>Category</span>
                <span className="font-bold text-zinc-800">{formData.category}</span>
              </div>
              <div className="flex justify-between items-center text-zinc-500 font-mono">
                <span>Rating</span>
                <span className="font-bold text-zinc-900 flex items-center gap-1">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                  {formData.overall_rating} / 5
                </span>
              </div>
              <div className="flex justify-between items-center text-zinc-500 font-mono">
                <span>Role</span>
                <span className="font-bold text-zinc-800">{formData.role}</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => setActiveTab('feed')}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold transition-all shadow-xs"
              >
                View Feedback Feed
              </button>
              <button
                type="button"
                onClick={handleResetForm}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-xs font-bold transition-all"
              >
                Submit Another Response
              </button>
            </div>
          </div>
        ) : (
          /* Feedback Form */
          <form onSubmit={handleSubmit} className="rounded-2xl p-6 sm:p-8 border border-zinc-200 bg-white space-y-6">
            
            {formError && (
              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{formError}</span>
              </div>
            )}

            {/* Submitter Role */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-zinc-900 uppercase font-mono tracking-wider">
                1. Your Role / Affiliation
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {ROLES.map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, role: r }))}
                    className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all text-center ${
                      formData.role === r
                        ? 'border-zinc-950 bg-zinc-950 text-white shadow-xs'
                        : 'border-zinc-200 bg-zinc-50 text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            {/* Name & Contact Info (Optional / Editable) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-zinc-900">
                  Full Name / Display Name <span className="text-zinc-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder={user ? user.display_name || user.username : 'e.g. Dr. Sharma or Rahul K.'}
                  className="w-full bg-zinc-50 border border-zinc-200 rounded-xl px-3.5 py-2.5 text-xs text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 placeholder:text-zinc-400"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-zinc-900">
                  Email / Roll Number <span className="text-zinc-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="e.g. faculty@kiit.ac.in or 2105xxx"
                  className="w-full bg-zinc-50 border border-zinc-200 rounded-xl px-3.5 py-2.5 text-xs text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 placeholder:text-zinc-400"
                />
              </div>
            </div>

            {/* Category Selector */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-zinc-900 uppercase font-mono tracking-wider">
                2. Feedback Category
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {CATEGORIES.map((cat) => {
                  const isSelected = formData.category === cat.id;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, category: cat.id }))}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        isSelected 
                          ? 'border-zinc-950 bg-zinc-950 text-white shadow-xs' 
                          : 'border-zinc-200 bg-white hover:border-zinc-300 hover:bg-zinc-50'
                      }`}
                    >
                      <p className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-zinc-900'}`}>
                        {cat.label}
                      </p>
                      <p className={`text-[11px] mt-0.5 ${isSelected ? 'text-zinc-300' : 'text-zinc-500'}`}>
                        {cat.desc}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Star Rating Section */}
            <div className="p-4 sm:p-5 rounded-2xl bg-zinc-50 border border-zinc-200/80 space-y-4">
              <div className="space-y-1">
                <label className="block text-xs font-bold text-zinc-900 uppercase font-mono tracking-wider">
                  3. Overall Satisfaction Rating
                </label>
                <p className="text-[11px] text-zinc-500">
                  How would you rate the overall concept, execution, and utility of HostelShare?
                </p>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex items-center gap-1.5">
                  {[1, 2, 3, 4, 5].map((star) => {
                    const isFilled = (hoverRating || formData.overall_rating) >= star;
                    return (
                      <button
                        key={star}
                        type="button"
                        onClick={() => handleRatingClick('overall_rating', star)}
                        onMouseEnter={() => setHoverRating(star)}
                        onMouseLeave={() => setHoverRating(0)}
                        className="p-1 rounded-lg hover:scale-110 transition-transform focus:outline-none"
                      >
                        <Star 
                          className={`w-7 h-7 sm:w-8 sm:h-8 transition-colors ${
                            isFilled 
                              ? 'fill-amber-400 text-amber-500' 
                              : 'text-zinc-300 hover:text-zinc-400'
                          }`} 
                        />
                      </button>
                    );
                  })}
                </div>

                <div className="text-xs font-mono font-bold text-zinc-800 px-3 py-1 bg-white rounded-lg border border-zinc-200 inline-block w-fit">
                  {formData.overall_rating} / 5 — {getRatingLabel(hoverRating || formData.overall_rating)}
                </div>
              </div>

              {/* Sub-ratings */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-zinc-200/80">
                {/* Ease of Use */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-zinc-700">Platform Ease of Use</span>
                    <span className="font-mono font-bold text-zinc-900">{formData.ease_of_use}/5</span>
                  </div>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map((num) => (
                      <button
                        key={num}
                        type="button"
                        onClick={() => handleRatingClick('ease_of_use', num)}
                        className={`flex-1 py-1 rounded-lg text-xs font-bold font-mono transition-all border ${
                          formData.ease_of_use >= num
                            ? 'bg-zinc-950 text-white border-zinc-950'
                            : 'bg-white text-zinc-400 border-zinc-200 hover:border-zinc-300'
                        }`}
                      >
                        {num}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Perceived Security & Handshake */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-zinc-700">Trust & Security (PIN Protocol)</span>
                    <span className="font-mono font-bold text-zinc-900">{formData.trust_safety}/5</span>
                  </div>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map((num) => (
                      <button
                        key={num}
                        type="button"
                        onClick={() => handleRatingClick('trust_safety', num)}
                        className={`flex-1 py-1 rounded-lg text-xs font-bold font-mono transition-all border ${
                          formData.trust_safety >= num
                            ? 'bg-zinc-950 text-white border-zinc-950'
                            : 'bg-white text-zinc-400 border-zinc-200 hover:border-zinc-300'
                        }`}
                      >
                        {num}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendation Question */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-zinc-900 uppercase font-mono tracking-wider">
                4. Would you recommend HostelShare to hostel students?
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {RECOMMEND_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, recommend: opt.value }))}
                    className={`p-2.5 rounded-xl border text-center transition-all ${
                      formData.recommend === opt.value
                        ? 'border-lime-500 bg-lime-50 text-zinc-950 ring-1 ring-lime-400'
                        : 'border-zinc-200 bg-white text-zinc-600 hover:border-zinc-300'
                    }`}
                  >
                    <p className="text-xs font-bold">{opt.label}</p>
                    <p className="text-[10px] text-zinc-400 font-mono mt-0.5">{opt.sub}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Detailed Remarks & Evaluation Text */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="block text-xs font-bold text-zinc-900 uppercase font-mono tracking-wider">
                  5. Detailed Feedback, Faculty Remarks & Suggestions <span className="text-rose-500">*</span>
                </label>
                <span className="text-[10px] font-mono text-zinc-400">
                  {formData.feedback_text.length} / 2000 chars
                </span>
              </div>
              <textarea
                rows={4}
                required
                value={formData.feedback_text}
                onChange={(e) => setFormData(prev => ({ ...prev, feedback_text: e.target.value }))}
                placeholder="Share your detailed feedback on project scope, UI workflow, utility sharing in hostellers' daily lives, safety verification, or suggestions for our next sprint..."
                className="w-full bg-zinc-50 border border-zinc-200 rounded-xl p-3.5 text-xs text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 placeholder:text-zinc-400 leading-relaxed resize-none"
              />
            </div>

            {/* Submit Button */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-[11px] text-zinc-400 font-mono">
                All evaluations are logged to the project review dashboard.
              </p>

              <button
                type="submit"
                disabled={submitting}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-zinc-950 hover:bg-zinc-800 disabled:bg-zinc-400 text-white text-xs font-bold transition-all shadow-xs"
              >
                {submitting ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Submitting Evaluation...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5 text-lime-400" />
                    <span>Submit Project Feedback</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )
      ) : (
        /* Feedback Feed / Review Wall */
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-white rounded-2xl border border-zinc-200">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-zinc-500" />
              <span className="text-xs font-bold text-zinc-800">Filter by Category:</span>
            </div>

            <div className="flex flex-wrap items-center gap-1.5">
              {['All', ...CATEGORIES.map(c => c.id)].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setFeedCategory(cat)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    feedCategory === cat
                      ? 'bg-zinc-950 text-white'
                      : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200 hover:text-zinc-900'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Feed List */}
          {feedLoading ? (
            <div className="p-12 text-center bg-white rounded-2xl border border-zinc-200">
              <div className="w-6 h-6 border-2 border-zinc-300 border-t-zinc-950 rounded-full animate-spin mx-auto mb-2" />
              <p className="text-xs text-zinc-500">Loading submitted feedback...</p>
            </div>
          ) : feedbacks.length === 0 ? (
            <div className="p-12 text-center bg-white rounded-2xl border border-zinc-200 space-y-3">
              <MessageSquare className="w-8 h-8 text-zinc-300 mx-auto" />
              <p className="text-sm font-bold text-zinc-800">No feedbacks in this category yet</p>
              <p className="text-xs text-zinc-500">Be the first to submit a review for HostelShare.</p>
              <button
                onClick={() => setActiveTab('form')}
                className="mt-2 px-4 py-2 bg-zinc-950 text-white rounded-xl text-xs font-bold hover:bg-zinc-800"
              >
                Submit Now
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3.5">
              {feedbacks.map((fb) => (
                <div 
                  key={fb.id}
                  className="p-5 bg-white rounded-2xl border border-zinc-200 space-y-3 hover:border-zinc-300 transition-all"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-zinc-100 text-zinc-800 font-bold flex items-center justify-center text-xs border border-zinc-200">
                        {fb.name ? fb.name[0].toUpperCase() : 'P'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-xs font-bold text-zinc-950">
                            {fb.user_display_name || fb.name || 'Anonymous Peer'}
                          </p>
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700 border border-zinc-200">
                            {fb.role || 'Student'}
                          </span>
                        </div>
                        <p className="text-[10px] font-mono text-zinc-400 flex items-center gap-1 mt-0.5">
                          <Clock className="w-2.5 h-2.5" />
                          <span>{new Date(fb.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-mono uppercase font-bold px-2.5 py-0.5 rounded-md bg-zinc-100 text-zinc-800 border border-zinc-200">
                        {fb.category}
                      </span>
                      <div className="flex items-center gap-1 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-md">
                        <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                        <span className="text-xs font-bold text-amber-900 font-mono">{fb.overall_rating}.0</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-zinc-700 leading-relaxed whitespace-pre-wrap">
                    {fb.feedback_text}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 pt-2 border-t border-zinc-100 text-[11px] font-mono text-zinc-500">
                    {fb.ease_of_use && (
                      <span>Ease of Use: <strong className="text-zinc-800">{fb.ease_of_use}/5</strong></span>
                    )}
                    {fb.trust_safety && (
                      <span>Safety Protocol: <strong className="text-zinc-800">{fb.trust_safety}/5</strong></span>
                    )}
                    {fb.recommend && (
                      <span>Recommend: <strong className="text-lime-700 bg-lime-50 px-1.5 py-0.5 rounded border border-lime-200">{fb.recommend}</strong></span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Faculty Notice Info Banner */}
      <div className="p-4 rounded-xl border border-zinc-200 bg-zinc-50 flex items-start gap-3 text-xs text-zinc-600">
        <Award className="w-4 h-4 text-zinc-700 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-zinc-900">Academic Project Compliance Note</p>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            This module fulfills the institutional criteria for real-time stakeholder feedback, user acceptance testing (UAT), and platform audit trails required for major project submissions.
          </p>
        </div>
      </div>

    </div>
  );
}

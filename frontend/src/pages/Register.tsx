import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Sparkles, Lock, Mail, User, ArrowRight } from "lucide-react";
import { UserRole } from "@/types/auth";

export const Register: React.FC<{ onNavigate: (path: string) => void }> = ({ onNavigate }) => {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<UserRole>("USER");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ email, password, full_name: fullName, role });
      onNavigate("home");
    } catch (err: any) {
      setError(err.response?.data?.message || "Registration failed. Please check password complexity rules.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-dark-surface/90 border border-dark-border rounded-3xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-400 text-white flex items-center justify-center mx-auto shadow-lg shadow-brand-500/20">
            <Sparkles className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-gray-100">Create Profile</h2>
          <p className="text-xs text-gray-400">Join the Cultural & Venue Smart Copilot Platform</p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500/40 rounded-xl text-xs text-red-300 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="reg-fullname" className="text-xs font-semibold text-gray-300 block mb-1">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                id="reg-fullname"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jordan Alex"
                className="w-full bg-dark-bg border border-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="reg-email" className="text-xs font-semibold text-gray-300 block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                id="reg-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jordan@example.com"
                className="w-full bg-dark-bg border border-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="reg-password" className="text-xs font-semibold text-gray-300 block mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                id="reg-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 chars, 1 uppercase, 1 symbol"
                className="w-full bg-dark-bg border border-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="reg-role" className="text-xs font-semibold text-gray-300 block mb-1">Account Role</label>
            <select
              id="reg-role"
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-brand-500"
            >
              <option value="USER">Visitor / Guest User</option>
              <option value="VOLUNTEER">Venue Volunteer Staff</option>
              <option value="ADMIN">Venue Operations Admin</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-bold text-sm rounded-xl shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {loading ? "Registering..." : "Create Account"}
            {!loading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div className="text-center text-xs text-gray-400">
          Already registered?{" "}
          <button onClick={() => onNavigate("login")} className="text-brand-400 hover:underline font-semibold">
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

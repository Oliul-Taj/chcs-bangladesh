'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldAlert, Activity, KeyRound } from 'lucide-react';

export default function Home() {
  const [identifier, setIdentifier] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleIdentityLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identity: identifier })
      });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || 'Something went wrong');
      router.push(data.redirect);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-md p-8 bg-slate-800 rounded-2xl border border-slate-700 shadow-xl">
        <div className="flex items-center space-x-3 mb-6 justify-center">
          <Activity className="h-8 w-8 text-emerald-400 animate-pulse" />
          <h1 className="text-2xl font-bold tracking-tight">CHCS Bangladesh</h1>
        </div>
        <p className="text-center text-slate-400 text-sm mb-6">
          Enter your NID, Birth Certificate, or Passport code without prefixes to query profiles securely.
        </p>

        <form onSubmit={handleIdentityLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Identification Input</label>
            <input 
              type="text"
              placeholder="e.g., 1988102938475 or EB-007"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl focus:outline-none focus:border-emerald-500 text-white transition-all text-center text-lg tracking-widest"
            />
          </div>

          {error && (
            <div className="flex items-center space-x-2 text-red-400 text-xs bg-red-950/50 p-3 rounded-lg border border-red-900">
              <ShieldAlert className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 font-medium rounded-xl text-slate-950 transition-colors disabled:opacity-50"
          >
            {loading ? 'Querying Records...' : 'Access Portal System'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-700/50 text-center flex justify-around text-xs text-slate-500">
          <a href="/ministry" className="hover:text-emerald-400 transition-colors">Ministry Node</a>
          <a href="/hospital" className="hover:text-emerald-400 transition-colors">Hospital Audit</a>
          <a href="/pharmacy" className="hover:text-emerald-400 transition-colors">Pharmacy Node</a>
        </div>
      </div>
    </div>
  );
}

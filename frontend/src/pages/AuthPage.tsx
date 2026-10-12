import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/components/ui/Toast";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { Card } from "@/components/ui/Card";
import { ArrowRight, Eye, EyeOff } from "lucide-react";

interface AuthPageProps {
  initialMode?: "login" | "register";
  onBackToLanding: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({
  initialMode = "register",
  onBackToLanding,
}) => {
  const { login, register } = useAuth();
  const { toast } = useToast();

  const [mode, setMode] = useState<"login" | "register">(initialMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      toast("Please fill in all required fields", "error");
      return;
    }

    if (mode === "register") {
      if (!fullName.trim()) {
        toast("Please provide your name", "error");
        return;
      }
      if (password.length < 8) {
        toast("Password must be at least 8 characters", "error");
        return;
      }
      if (password !== confirmPassword) {
        toast("Passwords do not match", "error");
        return;
      }
    }

    setIsSubmitting(true);
    try {
      if (mode === "register") {
        await register(email.trim(), password, fullName.trim());
        toast("Welcome to StudyPilot! Account created.", "success");
      } else {
        await login(email.trim(), password);
        toast("Welcome back!", "success");
      }
    } catch (err: any) {
      const msg = err?.error?.message || err?.detail || err?.message || "Authentication failed";
      toast(msg, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6F1] flex flex-col justify-between p-6 sm:p-10">
      {/* Top Header */}
      <header className="max-w-6xl mx-auto w-full flex items-center justify-between mb-8">
        <button
          onClick={onBackToLanding}
          className="flex items-center gap-3 text-left focus:outline-none"
        >
          <div className="w-8 h-8 rounded-lg bg-[#2F5D46] flex items-center justify-center text-white font-bold text-lg shadow-sm">
            S
          </div>
          <span className="font-bold text-xl tracking-tight text-[#1F2A24]">
            studypilot<span className="text-[#2F5D46]">.</span>
          </span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="text-xs font-semibold text-[#1F2A24] px-3 py-1.5 hover:text-[#2F5D46] transition-colors"
          >
            {mode === "login" ? "Create account" : "Sign in"}
          </button>
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="text-xs font-semibold text-white bg-[#2F5D46] hover:bg-[#254B38] px-3.5 py-1.5 rounded-lg transition-colors"
          >
            {mode === "login" ? "Get started" : "Sign in"}
          </button>
        </div>
      </header>

      {/* Main Split Layout (Matching Screenshot 4) */}
      <div className="max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center flex-1 my-auto">
        {/* Left Column */}
        <div className="lg:col-span-6 space-y-6 lg:pr-8">
          <Eyebrow>A better study rhythm</Eyebrow>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-[#1F2A24] leading-[1.15]">
            Make progress <br />
            feel manageable.
          </h1>
          <p className="text-base text-[#607166] leading-relaxed max-w-md">
            Bring your subjects, study sessions, and next steps into one thoughtful space.
          </p>
          <hr className="w-16 border-[#D7DEC5] pt-1" />
          <p className="text-xs text-[#8C9B90]">
            Plan thoughtfully. Practice often. Learn at your pace.
          </p>
        </div>

        {/* Right Column: Form Card */}
        <div className="lg:col-span-6 flex justify-center lg:justify-end">
          <Card className="w-full max-w-md p-8 sm:p-9 shadow-elevated">
            <Eyebrow>Create your space</Eyebrow>
            <h2 className="text-2xl font-bold text-[#1F2A24] mt-1 mb-1">
              {mode === "register" ? "Create your account" : "Sign in to your space"}
            </h2>
            <p className="text-xs text-[#607166] mb-6">
              {mode === "register"
                ? "A few details and you're ready to begin."
                : "Enter your credentials to continue your revision."}
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "register" && (
                <div>
                  <label className="text-xs font-medium text-[#1F2A24] block mb-1.5">
                    Your name
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="What should we call you?"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#E3E8E2] text-sm text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                  />
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-[#1F2A24] block mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#E3E8E2] text-sm text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-medium text-[#1F2A24]">
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-[11px] text-[#607166] hover:text-[#1F2A24] flex items-center gap-1"
                  >
                    {showPassword ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                    <span>{showPassword ? "Hide" : "Show"}</span>
                  </button>
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#E3E8E2] text-sm text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                />
              </div>

              {mode === "register" && (
                <div>
                  <label className="text-xs font-medium text-[#1F2A24] block mb-1.5">
                    Confirm password
                  </label>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Enter it once more"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#E3E8E2] text-sm text-[#1F2A24] placeholder:text-[#8C9B90] focus:outline-none focus:ring-2 focus:ring-[#2F5D46]/20 focus:border-[#2F5D46]"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-2 py-3 px-4 rounded-xl bg-[#2F5D46] hover:bg-[#254B38] text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm disabled:opacity-50"
              >
                <span>{isSubmitting ? "Please wait..." : mode === "register" ? "Create account" : "Sign in"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>

            {/* Toggle link */}
            <div className="mt-5 text-center">
              <button
                onClick={() => setMode(mode === "login" ? "register" : "login")}
                className="text-xs text-[#607166] hover:text-[#1F2A24]"
              >
                {mode === "register" ? (
                  <>Already have an account? <span className="font-semibold text-[#1F2A24]">Sign in</span></>
                ) : (
                  <>Don't have an account yet? <span className="font-semibold text-[#1F2A24]">Create account</span></>
                )}
              </button>
            </div>

            {/* Footnote matching screenshot 4 */}
            <div className="mt-6 pt-4 border-t border-[#E3E8E2] flex items-center gap-2 text-[11px] text-[#8C9B90]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] inline-block shrink-0"></span>
              <span>Prototype accounts are saved in this browser and backend database.</span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

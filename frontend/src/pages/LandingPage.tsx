import React from "react";
import { ArrowRight, Check, Sparkles } from "lucide-react";
import { Eyebrow } from "@/components/ui/Eyebrow";

interface LandingPageProps {
  onGetStarted: () => void;
  onSignIn: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onSignIn }) => {
  return (
    <div className="min-h-screen bg-[#F4F6F1] flex flex-col justify-between">
      {/* Top Navbar */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#2F5D46] flex items-center justify-center text-white font-bold text-lg shadow-sm">
            S
          </div>
          <span className="font-bold text-xl tracking-tight text-[#1F2A24]">
            studypilot<span className="text-[#2F5D46]">.</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onSignIn}
            className="text-sm font-medium text-[#1F2A24] hover:text-[#2F5D46] px-3 py-1.5 transition-colors"
          >
            Sign in
          </button>
          <button
            onClick={onGetStarted}
            className="text-sm font-semibold text-white bg-[#2F5D46] hover:bg-[#254B38] px-4 py-2 rounded-xl transition-all shadow-sm"
          >
            Get started
          </button>
        </div>
      </header>

      {/* Hero Section (Matching Screenshot 9) */}
      <main className="max-w-7xl mx-auto w-full px-6 py-12 lg:py-20 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center flex-1">
        {/* Left Column: Hero Copy */}
        <div className="lg:col-span-6 space-y-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#2F5D46]"></span>
            <Eyebrow>A personal learning space</Eyebrow>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#1F2A24] leading-[1.12]">
            Study with a plan{" "}
            <span className="text-[#2F5D46] font-editorial italic font-normal">
              that moves with you.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-[#607166] leading-relaxed max-w-lg">
            Build a steady learning rhythm, practice what you know, and make your next study session count.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={onGetStarted}
              className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#2F5D46] hover:bg-[#254B38] text-white rounded-xl text-sm font-semibold transition-all shadow-sm hover:shadow-md"
            >
              <span>Create your free account</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onSignIn}
              className="text-sm font-medium text-[#607166] hover:text-[#1F2A24] px-4 py-3.5 transition-colors"
            >
              I already have an account
            </button>
          </div>

          <p className="text-xs text-[#8C9B90] pt-2">
            Start with a subject. Adjust the plan as you go.
          </p>
        </div>

        {/* Right Column: Interactive Preview Card (Matching Screenshot 9) */}
        <div className="lg:col-span-6 flex justify-center lg:justify-end">
          <div className="w-full max-w-lg bg-white rounded-2xl border border-[#E3E8E2] p-6 sm:p-7 shadow-elevated">
            <div className="flex items-center justify-between mb-4">
              <Eyebrow>This week</Eyebrow>
              <span className="px-2.5 py-0.5 rounded-full bg-[#EBF2EC] text-[#2F5D46] text-[11px] font-medium border border-[#D7DEC5]">
                Example plan
              </span>
            </div>

            <h3 className="text-lg font-semibold text-[#1F2A24] mb-5">
              Your learning rhythm
            </h3>

            {/* Stat Counters */}
            <div className="grid grid-cols-3 gap-3 p-3 bg-[#F4F6F1] rounded-xl mb-5 text-center">
              <div>
                <span className="text-lg font-bold text-[#1F2A24] block">3</span>
                <span className="text-[10px] text-[#607166] uppercase tracking-wider block">sessions planned</span>
              </div>
              <div className="border-x border-[#E3E8E2]">
                <span className="text-lg font-bold text-[#1F2A24] block">2</span>
                <span className="text-[10px] text-[#607166] uppercase tracking-wider block">topics in focus</span>
              </div>
              <div>
                <span className="text-lg font-bold text-[#1F2A24] block">75</span>
                <span className="text-[10px] text-[#607166] uppercase tracking-wider block">minutes this week</span>
              </div>
            </div>

            {/* Weekday indicators */}
            <div className="flex items-center justify-between gap-1 mb-5">
              {[
                { day: "M", active: true },
                { day: "T", active: false },
                { day: "W", active: true },
                { day: "T", active: false },
                { day: "F", active: true },
                { day: "S", active: false },
                { day: "S", active: false },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className={`w-9 h-8 rounded-lg flex items-center justify-center text-xs font-semibold ${
                    item.active
                      ? "bg-[#EBF2EC] text-[#2F5D46] border border-[#D7DEC5]"
                      : "text-[#8C9B90] bg-[#F4F6F1]"
                  }`}
                >
                  {item.day}
                </div>
              ))}
            </div>

            {/* Planned Sessions List */}
            <div className="space-y-3 mb-5">
              <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-[#E3E8E2] border-l-4 border-l-[#2F5D46]">
                <div>
                  <span className="text-xs font-semibold text-[#1F2A24] block">Data structures</span>
                  <span className="text-[10px] text-[#607166]">Computer Engineering · Learn</span>
                </div>
                <span className="text-xs font-medium text-[#607166]">25 min</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-[#E3E8E2] border-l-4 border-l-[#10B981]">
                <div>
                  <span className="text-xs font-semibold text-[#1F2A24] block">Computer architecture</span>
                  <span className="text-[10px] text-[#607166]">Computer Engineering · Review</span>
                </div>
                <span className="text-xs font-medium text-[#607166]">15 min</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-[#E3E8E2] border-l-4 border-l-[#818CF8]">
                <div>
                  <span className="text-xs font-semibold text-[#1F2A24] block">Operating systems</span>
                  <span className="text-[10px] text-[#607166]">Computer Engineering · Learn</span>
                </div>
                <span className="text-xs font-medium text-[#607166]">35 min</span>
              </div>
            </div>

            {/* Bottom check guarantee */}
            <div className="flex items-center gap-2 text-xs text-[#2F5D46] font-medium pt-1">
              <Check className="w-3.5 h-3.5" />
              <span>Short sessions. Thoughtful reviews. Your own pace.</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer Ticker */}
      <footer className="border-t border-[#E3E8E2] bg-white py-6">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#607166]">
          <div className="flex items-center gap-6">
            <span className="font-semibold text-[#1F2A24] uppercase tracking-wider text-[11px]">
              Made for the way you learn
            </span>
            <span>01 Bayesian knowledge tracing</span>
            <span>02 Explainable daily queue</span>
            <span>03 Focus timer integration</span>
          </div>
          <span>StudyPilot © 2026</span>
        </div>
      </footer>
    </div>
  );
};

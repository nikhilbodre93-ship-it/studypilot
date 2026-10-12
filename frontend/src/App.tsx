import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Sidebar, NavItem } from "@/components/layout/Sidebar";
import { LandingPage } from "@/pages/LandingPage";
import { AuthPage } from "@/pages/AuthPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { MyLearningPage } from "@/pages/MyLearningPage";
import { PlanSetupPage } from "@/pages/PlanSetupPage";
import { RevisionPlannerPage } from "@/pages/RevisionPlannerPage";
import { FocusTimerPage } from "@/pages/FocusTimerPage";
import { ProgressPage } from "@/pages/ProgressPage";
import { NotesPage } from "@/pages/NotesPage";
import { QuizzesPage } from "@/pages/QuizzesPage";
import { FlashcardsPage } from "@/pages/FlashcardsPage";
import { RoadmapPage } from "@/pages/RoadmapPage";
import { AITutorPage } from "@/pages/AITutorPage";
import { QuestionPapersPage } from "@/pages/QuestionPapersPage";
import { Menu } from "lucide-react";

export const App: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [authView, setAuthView] = useState<"landing" | "login" | "register">("landing");
  const [currentTab, setCurrentTab] = useState<NavItem>("dashboard");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Focus timer prefill parameters when triggered from revision planner
  const [timerPrefill, setTimerPrefill] = useState<{
    subjectId?: number | null;
    topicId?: number | null;
    minutes?: number;
  }>({});

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F4F6F1] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#2F5D46] flex items-center justify-center text-white font-bold text-xl animate-pulse">
            S
          </div>
          <span className="text-xs text-[#607166] font-medium tracking-tight">
            Loading StudyPilot...
          </span>
        </div>
      </div>
    );
  }

  // Unauthenticated experience
  if (!isAuthenticated) {
    if (authView === "login" || authView === "register") {
      return (
        <AuthPage
          initialMode={authView}
          onBackToLanding={() => setAuthView("landing")}
        />
      );
    }
    return (
      <LandingPage
        onGetStarted={() => setAuthView("register")}
        onSignIn={() => setAuthView("login")}
      />
    );
  }

  // Handler for starting a focus session directly from revision planner
  const handleStartSession = (topicId: number, subjectId: number, minutes: number) => {
    setTimerPrefill({ topicId, subjectId, minutes });
    setCurrentTab("timer");
  };

  // Authenticated workspace experience
  return (
    <div className="min-h-screen bg-[#F4F6F1] flex">
      {/* Fixed Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-[260px] flex flex-col min-h-screen">
        {/* Mobile Top Navbar */}
        <header className="lg:hidden flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-sm border-b border-[#E3E8E2] sticky top-0 z-20">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#2F5D46] flex items-center justify-center text-white font-bold text-sm">
              S
            </div>
            <span className="font-bold text-base tracking-tight text-[#1F2A24]">
              studypilot<span className="text-[#2F5D46]">.</span>
            </span>
          </div>

          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-2 rounded-lg text-[#1F2A24] hover:bg-[#F4F6F1]"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 px-6 sm:px-10 py-8 max-w-7xl w-full">
          {currentTab === "dashboard" && <DashboardPage onNavigate={setCurrentTab} />}
          {currentTab === "learning" && <MyLearningPage onNavigate={setCurrentTab} />}
          {currentTab === "planner" && (
            <RevisionPlannerPage
              onNavigate={setCurrentTab}
              onStartSession={handleStartSession}
            />
          )}
          {currentTab === "roadmap" && <RoadmapPage onNavigate={setCurrentTab} />}
          {currentTab === "notes" && <NotesPage onNavigate={setCurrentTab} />}
          {currentTab === "quizzes" && <QuizzesPage onNavigate={setCurrentTab} />}
          {currentTab === "flashcards" && <FlashcardsPage onNavigate={setCurrentTab} />}
          {currentTab === "tutor" && <AITutorPage onNavigate={setCurrentTab} />}
          {currentTab === "timer" && (
            <FocusTimerPage
              initialSubjectId={timerPrefill.subjectId}
              initialTopicId={timerPrefill.topicId}
              initialMinutes={timerPrefill.minutes || 25}
            />
          )}
          {currentTab === "progress" && <ProgressPage />}
          {currentTab === "question_papers" && <QuestionPapersPage onNavigate={setCurrentTab} />}
        </main>
      </div>
    </div>
  );
};

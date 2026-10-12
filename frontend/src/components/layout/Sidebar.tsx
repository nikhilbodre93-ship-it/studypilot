import React from "react";
import { useAuth } from "@/context/AuthContext";
import { LogOut } from "lucide-react";

export type NavItem =
  | "dashboard"
  | "learning"
  | "planner"
  | "roadmap"
  | "notes"
  | "quizzes"
  | "flashcards"
  | "tutor"
  | "timer"
  | "progress"
  | "question_papers";


interface SidebarProps {
  currentTab: NavItem;
  onSelectTab: (tab: NavItem) => void;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

const NAV_ITEMS: { id: NavItem; num: string; label: string }[] = [
  { id: "dashboard", num: "01", label: "Dashboard" },
  { id: "learning", num: "02", label: "My learning" },
  { id: "planner", num: "03", label: "Revision planner" },
  { id: "roadmap", num: "04", label: "Learning roadmap" },
  { id: "notes", num: "05", label: "Study notes" },
  { id: "quizzes", num: "06", label: "Practice quizzes" },
  { id: "flashcards", num: "07", label: "Flashcards" },
  { id: "tutor", num: "08", label: "AI tutor" },
  { id: "timer", num: "09", label: "Focus timer" },
  { id: "progress", num: "10", label: "Progress" },
  { id: "question_papers", num: "11", label: "Exam papers" },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isOpenMobile,
  onCloseMobile,
}) => {
  const { user, logout } = useAuth();

  const handleNavClick = (tab: NavItem) => {
    onSelectTab(tab);
    if (onCloseMobile) onCloseMobile();
  };

  const initial = (user?.full_name || user?.email || "S")[0].toUpperCase();

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#F4F6F1] border-r border-[#E3E8E2] w-[260px] px-5 py-6 select-none">
      {/* Brand Logo */}
      <div className="flex items-center gap-3 px-2 mb-8">
        <div className="w-8 h-8 rounded-lg bg-[#2F5D46] flex items-center justify-center text-white font-bold text-lg shadow-sm">
          S
        </div>
        <span className="font-bold text-xl tracking-tight text-[#1F2A24]">
          studypilot<span className="text-[#2F5D46]">.</span>
        </span>
      </div>

      {/* Nav Eyebrow */}
      <div className="px-3 mb-2">
        <span className="text-[11px] font-semibold tracking-wider text-[#607166] uppercase">
          Your workspace
        </span>
      </div>

      {/* Navigation Items (01 - 10) */}
      <nav className="flex-1 space-y-1 overflow-y-auto pr-1">
        {NAV_ITEMS.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              className={`w-full flex items-center gap-3.5 px-3 py-2 rounded-xl text-sm transition-all duration-150 text-left ${
                isActive
                  ? "bg-[#EBF2EC] text-[#2F5D46] font-semibold"
                  : "text-[#607166] hover:text-[#1F2A24] hover:bg-[#ECEFE8] font-normal"
              }`}
            >
              <span
                className={`text-xs w-4 tracking-tighter ${
                  isActive ? "text-[#2F5D46] font-semibold" : "text-[#8C9B90]"
                }`}
              >
                {item.num}
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Area */}
      <div className="pt-4 border-t border-[#E3E8E2] mt-4 space-y-4">
        {/* Sync Status Indicator */}
        <div className="flex items-center gap-2 px-2 text-[11px] text-[#607166]">
          <span className="w-2 h-2 rounded-full bg-[#10B981] inline-block animate-pulse"></span>
          <span>Your progress is saved on this device</span>
        </div>

        {/* User Card */}
        <div className="flex items-center justify-between px-2 pt-1">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-[#EBF2EC] border border-[#D7DEC5] text-[#2F5D46] font-semibold flex items-center justify-center text-xs shrink-0">
              {initial}
            </div>
            <div className="flex flex-col truncate">
              <span className="text-xs font-semibold text-[#1F2A24] truncate">
                {user?.full_name || "Student"}
              </span>
              <span className="text-[10px] text-[#8C9B90] truncate max-w-[110px]">
                {user?.email || "student@studypilot.io"}
              </span>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-[11px] text-[#607166] hover:text-[#DC2626] transition-colors shrink-0 font-medium"
            title="Sign out"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside className="hidden lg:block fixed left-0 top-0 bottom-0 z-30">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/30 backdrop-blur-sm"
            onClick={onCloseMobile}
          />
          <div className="relative z-50">{sidebarContent}</div>
        </div>
      )}
    </>
  );
};

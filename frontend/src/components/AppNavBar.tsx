"use client";
/**
 * 画面最左端のアイコン専用縦並びナビゲーションバー。
 * Slack の App サイドバー相当。
 */

import { Bot, Hash, MessageCircle, Search, Settings } from "lucide-react";

export type NavSection = "channels" | "dms" | "bots";

interface Props {
  activeSection: NavSection;
  onSectionChange: (section: NavSection) => void;
  onSearchClick: () => void;
  onSettingsClick: () => void;
  /** ワークスペース名の頭文字（アイコン代わり） */
  workspaceLetter?: string;
}

interface NavButtonProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick: () => void;
}

function NavButton({ icon, label, active, onClick }: NavButtonProps) {
  return (
    <button
      onClick={onClick}
      title={label}
      aria-label={label}
      className={`
        relative flex items-center justify-center w-10 h-10 rounded-xl
        transition-all duration-150 group
        ${
          active
            ? "bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white shadow-lg shadow-violet-500/30 glow-primary"
            : "text-gray-400 hover:text-white hover:bg-white/10"
        }
      `}
    >
      {icon}
      {/* アクティブインジケーター（左縁のライン） */}
      {active && (
        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-white rounded-r-full -ml-2" />
      )}
      {/* ツールチップ */}
      <span
        className="
          pointer-events-none absolute left-full ml-3 px-2 py-1
          text-xs text-white bg-gray-900/95 rounded-md whitespace-nowrap
          opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50
          border border-white/10 shadow-lg
        "
      >
        {label}
      </span>
    </button>
  );
}

export default function AppNavBar({
  activeSection,
  onSectionChange,
  onSearchClick,
  onSettingsClick,
  workspaceLetter = "P",
}: Props) {
  return (
    <nav className="w-14 flex flex-col items-center gap-1.5 py-3 bg-gray-950 border-r border-violet-500/10 h-full">
      {/* ワークスペースアイコン */}
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-500 flex items-center justify-center text-white font-bold text-base shadow-md mb-2 cursor-default select-none">
        {workspaceLetter}
      </div>

      <div className="w-8 h-px bg-white/8 mb-1" />

      {/* チャンネル */}
      <NavButton
        icon={<Hash size={18} />}
        label="チャンネル"
        active={activeSection === "channels"}
        onClick={() => onSectionChange("channels")}
      />

      {/* ダイレクトメッセージ */}
      <NavButton
        icon={<MessageCircle size={18} />}
        label="ダイレクトメッセージ"
        active={activeSection === "dms"}
        onClick={() => onSectionChange("dms")}
      />

      {/* ボット管理 */}
      <NavButton
        icon={<Bot size={18} />}
        label="ボット管理"
        active={activeSection === "bots"}
        onClick={() => onSectionChange("bots")}
      />

      {/* 検索 */}
      <NavButton
        icon={<Search size={18} />}
        label="検索"
        active={false}
        onClick={onSearchClick}
      />

      {/* スペーサー */}
      <div className="flex-1" />

      <div className="w-8 h-px bg-white/8 mb-1" />

      {/* 設定 */}
      <NavButton
        icon={<Settings size={18} />}
        label="設定・プロフィール"
        active={false}
        onClick={onSettingsClick}
      />
    </nav>
  );
}

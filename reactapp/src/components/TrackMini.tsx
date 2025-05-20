import React from "react";
import { NowPlayContext } from "@/routes/playpage";

import type { TrackData } from "@/APIs/PlaylistService";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { CirclePause, CirclePlay, EllipsisVertical, Trash } from "lucide-react";
import PlaylistService from "@/APIs/PlaylistService";

function timeConvert(sec: number | undefined): string {
  if (typeof sec !== "number" || isNaN(sec) || sec < 0) return "00:00";
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

type Props = {
  track: TrackData;
  for_w: "playlist" | "recommendations";
};

const TrackMini: React.FC<Props> = ({ track, for_w }) => {
  const state = React.useContext(NowPlayContext);
  const link = "https://youtu.be/" + track.yt_id;
  const bgUrl = `https://img.youtube.com/vi/${track.yt_id}/mqdefault.jpg`;

  const removeTrack = async () => {
    if (
      await PlaylistService.removeTrackFromPlaylist(state.playlist_id, track.id)
    ) {
      state.setPlaylistContent(
        state.playlistContent.filter((t) => t.id !== track.id)
      );
    }
  };
  const addToPlaylist = async () => {
    if (await PlaylistService.addTrackToPlaylist(state.playlist_id, link)) {
      state.setPlaylistContent([...state.playlistContent, track]);
    }
  };

  return (
    <div className="w-full h-12 mt-2">
      <div className="relative w-full h-12 overflow-hidden rounded-md">
        {/* Фоновая картинка с размытием */}
        <div
          className="absolute inset-0 bg-cover bg-center blur-none"
          style={{
            backgroundImage: `url('${bgUrl}')`,
          }}
        />

        {/* Полупрозрачная тень сверху, если надо затемнить */}
        <div className="absolute inset-0 bg-black/55" />

        {/* Контент-контейнер */}
        <div className="relative z-10 post_mini rounded-md h-12">
          <button
            className=" number_mini"
            type="button"
            onClick={() => {
              if (state.nowPlay === track.yt_id) {
                state.setNowPlay("");
              } else {
                state.setNowPlay(track.yt_id);
              }
            }}
          >
            {state.nowPlay === track.yt_id ? (
              <CirclePause color="red" size={30} strokeWidth="1.5" />
            ) : (
              <CirclePlay size={30} strokeWidth="1" />
            )}
          </button>

          <div className="description_mini text-xs truncate">
            <ul className="w-full">
              <li className="flex justify-start">
                <strong>{track.title}</strong>
              </li>
              <li className="flex justify-start text-[#b9b9b9a4]">
                {timeConvert(track.duration)} {track.artist}
              </li>
            </ul>
          </div>

          <div className="dropdown_mini">
            <DropdownMenu>
              <DropdownMenuTrigger className="w-10 h-full flex justify-center items-center">
                <EllipsisVertical size={20} />
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-gray-600 text-white">
                <DropdownMenuItem>
                  <a href={link}>Відкрити на YouTube</a>
                </DropdownMenuItem>
                {for_w === "playlist" ? (
                  <DropdownMenuItem
                    className="bg-red-700"
                    onClick={removeTrack}
                  >
                    Вилучити з плейлисту
                  </DropdownMenuItem>
                ) : (
                  <DropdownMenuItem onClick={addToPlaylist}>
                    Додати в плейлист
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrackMini;

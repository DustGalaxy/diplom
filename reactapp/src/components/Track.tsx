import React from "react";
import { NowPlayContext } from "../routes/playpage";

import type { TrackData } from "@/APIs/PlaylistService";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
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

const Track: React.FC<Props> = ({ track, for_w }) => {
  const state = React.useContext(NowPlayContext);
  const link = "https://youtu.be/" + track.yt_id;

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
    <div className="post  bg-gray-600 p-1 rounded-xl">
      <button
        className="number"
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
          <CirclePause size={50} strokeWidth="1" />
        ) : (
          <CirclePlay size={50} strokeWidth="1" />
        )}
      </button>

      <div className="relative  img-conteiner">
        <img
          className="image"
          src={"https://img.youtube.com/vi/" + track.yt_id + "/mqdefault.jpg"}
        />
        <div className="absolute  bottom-[3px] right-[3px] px-2 rounded-xl  bg-[#000000a7]">
          {timeConvert(track.duration)}
        </div>
      </div>

      <div className="post-description">
        <ul className="w-full">
          <li className="flex justify-start text-xl">
            <strong>{track.title}</strong>
          </li>
          <li className="flex justify-start text-xl text-[#b9b9b9a4]">
            {track.artist}
          </li>
        </ul>
      </div>
      <div className="dropdown">
        <DropdownMenu>
          <DropdownMenuTrigger className="w-10 h-full flex justify-center items-center">
            <EllipsisVertical size={32} />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-600 text-white">
            <DropdownMenuItem>
              <a href={link}>Відкрити на YouTube</a>
            </DropdownMenuItem>
            {for_w === "playlist" ? (
              <DropdownMenuItem className="bg-red-700" onClick={removeTrack}>
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
  );
};

export default Track;

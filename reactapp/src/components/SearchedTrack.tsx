import React from "react";
import { NowPlayContext } from "./TrackList";

import type { TrackData } from "@/APIs/PlaylistService";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { CirclePause, CirclePlay, EllipsisVertical, Info } from "lucide-react";
import StatService from "@/APIs/StatService";

function timeConvert(sec: number | undefined): string {
  if (typeof sec !== "number" || isNaN(sec) || sec < 0) return "00:00";
  const minutes = Math.floor(sec / 60);
  const seconds = Math.floor(sec % 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

type Props = {
  track: TrackData;
};

const Track: React.FC<Props> = ({ track }) => {
  const state = React.useContext(NowPlayContext);
  const link = "https://youtu.be/" + track.yt_id;
  const [listensData, setListensData] = React.useState<number>(0);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(link);
  };

  const getListens = async () => {
    const listens = await StatService.getStatByTrack(track.yt_id);
    if (listens === null) return;
    setListensData(listens);
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
        <DropdownMenu
          onOpenChange={(open) => {
            if (open) getListens();
          }}
        >
          <DropdownMenuTrigger className="w-10 h-full flex justify-center items-center">
            <Info />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-600 text-white">
            <DropdownMenuItem>Прослухали: {listensData}</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <DropdownMenu>
          <DropdownMenuTrigger className="w-10 h-full flex justify-center items-center">
            <EllipsisVertical size={32} />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-600 text-white">
            <DropdownMenuItem>
              <a href={link}>Відкрити на YouTube</a>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={copyToClipboard}>
              Копіювати посилання
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

export default Track;

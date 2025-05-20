import React from "react";

import type { TrackData } from "@/APIs/PlaylistService";
import SearchedTrack from "./SearchedTrack";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import PlaylistService from "@/APIs/PlaylistService";
import YoutubePlayer from "./YoutubePlayer";
import useWindowDimensions from "@/hooks/useWindowDimensions";
import SearchedTrackMini from "./SearchedTrackMini";
import StatService from "@/APIs/StatService";

export type state = {
  nowPlay: string;
  setNowPlay: React.Dispatch<React.SetStateAction<string>>;
};

export const NowPlayContext = React.createContext<state>({} as state);

const TrackList: React.FC = () => {
  const [tracks, setTracks] = React.useState<TrackData[]>([]);
  const [filter, setFilter] = React.useState("");
  const [nowPlay, setNowPlay] = React.useState<string>("");
  const { height, width } = useWindowDimensions();

  const findTracks = async () => {
    const tracks = await PlaylistService.getTracksByQuery(filter);
    if (tracks) {
      setTracks(tracks);
    }
  };
  const nextTrack = async () => {
    const index = tracks.findIndex((track) => track.yt_id === nowPlay);
    if (index >= tracks.length - 1) {
      setNowPlay(tracks[0].yt_id);
    } else {
      setNowPlay(tracks[index + 1].yt_id);
    }
    void StatService.sendListenData(nowPlay);
  };
  return (
    <div>
      <NowPlayContext.Provider
        value={{ nowPlay: nowPlay, setNowPlay: setNowPlay }}
      >
        <div
          className={`w-full flex justify-center p-4 ${!nowPlay && "hidden"}`}
        >
          <YoutubePlayer nextVideo={nextTrack} nowPlay={nowPlay} />
        </div>
        <div className="flex mb-2 md:mb-4">
          <Button
            onClick={findTracks}
            disabled={!filter}
            variant={"ghost"}
            className=" bg-gray-600 mr-4 "
          >
            Знайти
          </Button>
          <Input
            placeholder="Назва трека"
            onChange={(e) => setFilter(e.target.value)}
            value={filter}
            className="text-sm md:text-base"
          />
        </div>
        <div>
          {width > 650
            ? tracks.map((track, i) => <SearchedTrack track={track} key={i} />)
            : tracks.map((track, i) => (
                <SearchedTrackMini track={track} key={i} />
              ))}
        </div>
      </NowPlayContext.Provider>
    </div>
  );
};

export default TrackList;

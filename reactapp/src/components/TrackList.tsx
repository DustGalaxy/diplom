import React from "react";

import type { TrackData } from "@/APIs/PlaylistService";
import SearchedTrack from "./SearchedTrack";

import YoutubePlayer from "./YoutubePlayer";
import useWindowDimensions from "@/hooks/useWindowDimensions";
import SearchedTrackMini from "./SearchedTrackMini";

export type state = {
  nowPlay: string;
  setNowPlay: React.Dispatch<React.SetStateAction<string>>;
};

export const NowPlayContext = React.createContext<state>({} as state);

type Props = {
  tracks_: TrackData[];
};
const TrackList: React.FC<Props> = ({ tracks_ }) => {
  const [nowPlay, setNowPlay] = React.useState<string>("");
  const { height, width } = useWindowDimensions();

  const nextTrack = async () => {
    const index = tracks_.findIndex((track) => track.yt_id === nowPlay);
    if (index >= tracks_.length - 1) {
      setNowPlay(tracks_[0].yt_id);
    } else {
      setNowPlay(tracks_[index + 1].yt_id);
    }
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
        {tracks_.length > 0 && (
          <div>
            {width > 650
              ? tracks_.map((track, i) => (
                  <SearchedTrack track={track} key={i} />
                ))
              : tracks_.map((track, i) => (
                  <SearchedTrackMini track={track} key={i} />
                ))}
          </div>
        )}
      </NowPlayContext.Provider>
    </div>
  );
};

export default TrackList;

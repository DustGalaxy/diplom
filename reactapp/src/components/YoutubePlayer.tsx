import React, { useContext } from "react";
import YouTube from "react-youtube";
import type { YouTubeProps, YouTubeEvent } from "react-youtube";
import useWindowDimensions from "@/hooks/useWindowDimensions";
import StatService from "@/APIs/StatService";

type YoutubePlayerProps = {
  nextVideo: () => void;
  nowPlay: string;
};

const YoutubePlayer: React.FC<YoutubePlayerProps> = ({
  nextVideo,
  nowPlay,
}) => {
  const { height, width } = useWindowDimensions();
  const opts: YouTubeProps["opts"] = {
    height: width > 650 ? "360" : "180",
    width: width > 650 ? "640" : "310",
    playerVars: {
      autoplay: 1,
      start: 0,
      rel: 0,
      origin: "http://localhost:3000",
    },
  };

  const _onReady = async (event: YouTubeEvent<any>): Promise<void> => {
    if (!nowPlay) return;
    const sleep = (ms: number) =>
      new Promise((resolve) => setTimeout(resolve, ms));
    await sleep(10);
    event.target.playVideo();
    event.target.seekTo(0);

    void StatService.sendClickTrack(nowPlay);
  };

  return (
    <YouTube
      videoId={nowPlay || ""}
      opts={opts}
      onReady={_onReady}
      onEnd={() => {
        nextVideo();
        void StatService.sendListenData(nowPlay);
      }}
    />
  );
};

export default YoutubePlayer;

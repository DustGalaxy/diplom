import axios from "axios";
import { BASIC_API_URL } from "@/main";

export type RegesterData = {
  username: string;
  email: string;
  password: string;
};

export default class StatService {
  static async getStatByTrack(track_yt_id: string): Promise<number | null> {
    try {
      const response = await axios.get(`${BASIC_API_URL}/track/stat`, {
        withCredentials: true,
        params: {
          yt_id: track_yt_id,
        },
      });
      return response.status === 200 ? response.data.track_playback : null;
    } catch (error) {
      return null;
    }
  }

  static async getDateAddToPlaylist(
    track_id: string,
    playlist_id: string
  ): Promise<Date | null> {
    try {
      const response = await axios.get(`${BASIC_API_URL}/track_plst/stat`, {
        withCredentials: true,
        params: {
          playlist_id: playlist_id,
          track_id: track_id,
        },
      });
      return response.status === 200
        ? new Date(response.data.in_playlist_since)
        : null;
    } catch (error) {
      return null;
    }
  }

  static async sendListenData(track_yt_id: string): Promise<void> {
    try {
      await axios.post(
        `${BASIC_API_URL}/track/stat`,
        {
          id: track_yt_id,
        },
        {
          withCredentials: true,
        }
      );
    } catch (error) {}
  }
}

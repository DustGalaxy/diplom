import axios from "axios";
import { BASIC_API_URL } from "@/main";

type PlaylistMeta = {
  id: string;
  name: string;
  tracks_amount: number;
};

export type TrackData = {
  id: string;
  title: string;
  yt_id: string;
  duration: number;
  artist: string;
  score: number | null;
};

export default class PlaylistService {
  static async getPlaylists(): Promise<PlaylistMeta[]> {
    try {
      const response = await axios.get(`${BASIC_API_URL}/playlists`, {
        withCredentials: true,
      });
      return response.status === 200 ? (response.data as PlaylistMeta[]) : [];
    } catch {
      return [];
    }
  }

  static async getTracks(playlistId: string): Promise<TrackData[]> {
    try {
      const response = await axios.get(
        `${BASIC_API_URL}/playlists/${playlistId}`,
        {
          withCredentials: true,
        }
      );
      return response.status === 200 ? (response.data as TrackData[]) : [];
    } catch {
      return [];
    }
  }

  static async getTracksByQuery(query: string): Promise<TrackData[]> {
    try {
      const response = await axios.get(
        `${BASIC_API_URL}/tracks?query=${query}`
      );
      return response.status === 200 ? (response.data as TrackData[]) : [];
    } catch {
      return [];
    }
  }

  static async addTrackToPlaylist(
    playlistId: string,
    yt_url: string
  ): Promise<TrackData | null> {
    try {
      const response = await axios.post(
        `${BASIC_API_URL}/playlists/add_track`,
        {
          playlist_id: playlistId,
          yt_url: yt_url,
        },

        {
          withCredentials: true,
        }
      );
      return response.status === 200 ? response.data : null;
    } catch {
      return null;
    }
  }

  static async removeTrackFromPlaylist(
    playlistId: string,
    trackId: string
  ): Promise<boolean> {
    try {
      const response = await axios.delete(
        `${BASIC_API_URL}/playlists/${playlistId}/remove_track?track_id=${trackId}`,
        {
          withCredentials: true,
        }
      );
      return response.status === 204 ? true : false;
    } catch {
      return false;
    }
  }

  static async newPlaylist(name: string): Promise<PlaylistMeta | null> {
    try {
      const response = await axios.post(
        `${BASIC_API_URL}/playlists`,
        { name: name },
        {
          withCredentials: true,
        }
      );
      return response.status === 201 ? (response.data as PlaylistMeta) : null;
    } catch (error) {
      return null;
    }
  }

  static async renamePlaylist(
    newname: string,
    id: string
  ): Promise<PlaylistMeta | null> {
    try {
      const response = await axios.put(
        `${BASIC_API_URL}/playlists/${id}`,
        { name: newname },
        {
          withCredentials: true,
        }
      );
      return response.status === 200 ? (response.data as PlaylistMeta) : null;
    } catch (error) {
      return null;
    }
  }

  static async deletePlaylist(name: string): Promise<boolean> {
    try {
      await axios.delete(`${BASIC_API_URL}/playlists?name=${name}`, {
        withCredentials: true,
      });
      return true;
    } catch (error) {
      return false;
    }
  }

  static async getRecommendations(
    plst_id: string
  ): Promise<TrackData[] | null> {
    try {
      const response = await axios.get(
        `${BASIC_API_URL}/playlists/${plst_id}/recommendations`,
        {
          withCredentials: true,
        }
      );
      return response.status === 200 ? (response.data as TrackData[]) : null;
    } catch (error) {
      return null;
    }
  }
}

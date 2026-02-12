import axios from "axios";


interface UserLogin {
    email:string
    password:string
}
export default function admin() {
  const adminLogin = async (formData:UserLogin) => {
    try {


      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/admin_auth/login`,
        formData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      // return response.status

      return response;
    } catch (error) {
      console.error("Failed to send user info:", error);
      return null;
    }
  };
const refreshAccessToken = async (refreshToken: string) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/get_access_token_from_refresh_token`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: refreshToken || '', // ⬅ IMPORTANT
    },
  });

  if (!res.ok) throw new Error("Failed to refresh token");

  const data = await res.json(); 
  return data.token; // returns *only access token*
};


  return {
    adminLogin,
    refreshAccessToken,
  };
}

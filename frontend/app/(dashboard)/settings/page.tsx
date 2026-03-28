"use client";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

type User = {
  email: string;
  profile_photo_url: string;
  username: string;
};

const DashboardPage = () => {
  const [userDetail, setdetail] = useState<User | null>(null);
  const [profile_photo, set_Photo] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      set_Photo(e.target.files[0]); // ✅ store file directly
    }
  };

  const uploadImage = async () => {
    if (!profile_photo) return;

    const formData = new FormData();
    formData.append("file", profile_photo);

    const res = await fetch(
      "http://localhost:8000/upload-file?file_type=profile_photo",
      {
        method: "POST",
        body: formData,
        credentials: "include",
      },
    );

    const data = await res.json();
    console.log(data);

    // update state with new image URL
    setdetail((prev) => ({
      ...prev!,
      profile_photo_url: data.url,
    }));

    // optional: clear file
    set_Photo(null);
  };

  useEffect(() => {
    const fetchUser = async () => {
      const res = await fetch(`http://localhost:8000/user-details`, {
        cache: "no-store",
        credentials: "include",
      });
      if (res.status === 401) {
        window.location.href = "/login";
      }

      if (!res.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await res.json();
      console.log("Data===>", data);
      setdetail({
        email: data.email,
        profile_photo_url: data.profile_photo,
        username: data.username,
      });
    };

    fetchUser();
  }, []);

  return (
    <div>
      <div className="text-black text-3xl pt-12 pb-3">Settings</div>
      <div className="mb-2">
        <div className="border text-black border-gray-300 h-100 rounded-md pl-4">
          <span className="text-2xl">Profile Image</span>
          <div className="mt-auto flex items-center gap-2 px-2 text-gray-500 pl-4 pb-2">
            <img
              src={
                userDetail?.profile_photo_url
                  ? userDetail.profile_photo_url
                  : "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
              }
              className="w-40 h-40 rounded-full"
            />
          </div>
          <form className="space-y-6 max-w-md">
            {/* File Input */}
            <div>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              onClick={uploadImage}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Upload Image
            </button>
          </form>
        </div>
      </div>
      <div className="border text-black border-gray-300 h-80 rounded-md pl-4">
        <span className="text-2xl">Change Password</span>
        <form className="max-w-md mx-auto space-y-6">
          {/* Current Password */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Current Password
            </label>
            <input
              type="password"
              placeholder="Enter current password"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* New Password */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              New Password
            </label>
            <input
              type="password"
              placeholder="Enter new password"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              placeholder="Confirm new password"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg 
               hover:bg-blue-700 transition"
          >
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default DashboardPage;

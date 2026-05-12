"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User, Lock, Upload, Camera, AlertCircle, CheckCircle } from "lucide-react";

type UserType = {
  email: string;
  profile_photo_url: string;
  username: string;
};

const DashboardPage = () => {
  const router = useRouter();
  const [userDetail, setdetail] = useState<UserType | null>(null);
  const [profile_photo, set_Photo] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [uploadMsg, setUploadMsg] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const [pwdMsg, setPwdMsg] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      set_Photo(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const uploadImage = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!profile_photo) return;
    const formData = new FormData();
    formData.append("file", profile_photo);
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/upload-file?file_type=profile_photo`,
      { method: "POST", body: formData, credentials: "include" }
    );
    const data = await res.json();
    setdetail((prev) => ({ ...prev!, profile_photo_url: data.url }));
    set_Photo(null);
    setPhotoPreview(null);
    setUploadMsg({ type: "success", text: "Profile photo updated!" });
    setTimeout(() => window.location.reload(), 1500);
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = {
      current_password: formData.get("current_password")?.toString().trim(),
      new_password: formData.get("new_password")?.toString().trim(),
      confirm_new_password: formData
        .get("confirm_new_password")
        ?.toString()
        .trim(),
    };
    if (
      !data.current_password ||
      !data.new_password ||
      !data.confirm_new_password
    ) {
      setPwdMsg({ type: "error", text: "All fields are required" });
      return;
    }
    if (data.new_password !== data.confirm_new_password) {
      setPwdMsg({ type: "error", text: "Passwords do not match" });
      return;
    }
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/change-password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(data),
        }
      );
      const result = await res.json();
      if (!res.ok) {
        setPwdMsg({ type: "error", text: result.message || "Error" });
        return;
      }
      setPwdMsg({ type: "success", text: "Password updated successfully!" });
      form.reset();
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setPwdMsg({ type: "error", text: "Something went wrong" });
    }
  };

  useEffect(() => {
    const fetchUser = async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/user-details`,
        { cache: "no-store", credentials: "include" }
      );
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (!res.ok) throw new Error("Failed to fetch data");
      const data = await res.json();
      setdetail({
        email: data.email,
        profile_photo_url: data.profile_photo_url,
        username: data.username,
      });
    };
    fetchUser();
  }, []);

  const inputClass =
    "w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-gray-400 bg-gray-50/50 transition-colors";

  const InlineMsg = ({
    msg,
  }: {
    msg: { type: "success" | "error"; text: string } | null;
  }) =>
    msg ? (
      <div
        className={`flex items-center gap-2 text-sm rounded-xl px-4 py-2.5 ${
          msg.type === "success"
            ? "bg-green-50 text-green-700 border border-green-100"
            : "bg-red-50 text-red-700 border border-red-100"
        }`}
      >
        {msg.type === "success" ? (
          <CheckCircle size={14} />
        ) : (
          <AlertCircle size={14} />
        )}
        {msg.text}
      </div>
    ) : null;

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500 mt-1">
          Manage your profile and account security
        </p>
      </div>

      {/* Profile Photo Card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <div className="flex items-center gap-2 mb-5">
          <User size={15} className="text-gray-400" />
          <h2 className="text-base font-semibold text-gray-900">
            Profile Photo
          </h2>
        </div>

        <div className="flex items-center gap-5">
          <div className="relative flex-shrink-0">
            <img
              src={
                photoPreview ||
                userDetail?.profile_photo_url ||
                "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
              }
              className="w-20 h-20 rounded-2xl object-cover ring-4 ring-gray-100"
              alt="Profile"
            />
            <label className="absolute -bottom-1.5 -right-1.5 w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-indigo-700 transition shadow-sm shadow-indigo-200">
              <Camera size={13} className="text-white" />
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">
              {userDetail?.username || "Loading…"}
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              {userDetail?.email || "No email linked"}
            </p>
            {profile_photo && (
              <button
                type="button"
                onClick={uploadImage}
                className="inline-flex items-center gap-1.5 mt-3 bg-indigo-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition shadow-sm"
              >
                <Upload size={12} />
                Upload Photo
              </button>
            )}
            {!profile_photo && (
              <p className="text-xs text-gray-400 mt-2">
                Click the camera icon to change your photo
              </p>
            )}
          </div>
        </div>

        {uploadMsg && (
          <div className="mt-4">
            <InlineMsg msg={uploadMsg} />
          </div>
        )}
      </div>

      {/* Change Password Card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-5">
          <Lock size={15} className="text-gray-400" />
          <h2 className="text-base font-semibold text-gray-900">
            Change Password
          </h2>
        </div>

        <form className="space-y-4 max-w-sm" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">
              Current Password
            </label>
            <input
              type="password"
              name="current_password"
              placeholder="Enter current password"
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">
              New Password
            </label>
            <input
              type="password"
              name="new_password"
              placeholder="Enter new password"
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">
              Confirm Password
            </label>
            <input
              type="password"
              name="confirm_new_password"
              placeholder="Confirm new password"
              className={inputClass}
            />
          </div>

          {pwdMsg && <InlineMsg msg={pwdMsg} />}

          <button
            type="submit"
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition shadow-sm shadow-indigo-200"
          >
            <Lock size={13} />
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
};

export default DashboardPage;

"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

const SignUPPage = () => {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);

    const data = {
      name: formData.get("name")?.toString().trim(),
      email: formData.get("email")?.toString().trim(),
      password: formData.get("password")?.toString().trim(),
    };

    // 🔴 validation
    if (!data.name || !data.email || !data.password) {
      alert("All fields are required");
      return;
    }

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/create-user`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(data), // ✅ fixed
        },
      );

      const result = await res.json();

      if (!res.ok) {
        alert(result.message || "Signup failed");
        return;
      }

      console.log(result);

      // ✅ redirect after success
      router.push("/home");
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="text-black text-3xl font-semibold mb-6">
        Email Intelligence Dashboard
      </div>

      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Create Your account
        </h2>

        {/* ✅ attach onSubmit here */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text" // ✅ fixed
              name="name"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="Username"
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              name="email"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="your@email.com"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              name="password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="••••••••"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="flex items-center">
            <input type="checkbox" className="mr-2" />
            <span className="text-sm text-gray-600">Remember me</span>
          </div>

          {/* ✅ button should be submit */}
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Sign up
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignUPPage;

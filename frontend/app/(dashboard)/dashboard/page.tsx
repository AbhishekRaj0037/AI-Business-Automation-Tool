import Image from "next/image";
import Link from "next/link";
const DashboardPage = () => {
  return (
    <div>
      <div className="text-black text-3xl pl-12 pt-12">
        Email Intelligence -Today
      </div>
      <div className="text-black text-l pl-12 pt-4">
        Real-time visibility into inbox activity and AI workload
      </div>
      <div className="flex pl-12 gap-4 pt-5 ">
        <div className="rounded-md bg-blue-100 p-4 text-black w-64 h-35">
          <Image src="/email.png" alt="" width={40} height={40} />
          <div>Email Fetched Today</div>
          <div className="text-3xl">128</div>
          <div>
            <span className="text-green-600">+12%</span> vs yesterday
          </div>
        </div>
        <div className="rounded-md bg-blue-100  p-4 text-black w-64 h-35">
          <Image
            src="/artificial-intelligence.png"
            alt=""
            width={40}
            height={40}
          />
          <div>Sent to AI Analysis</div>
          <div className="text-3xl">94</div>
          <div>73% processed</div>
        </div>
        <div className="rounded-md bg-blue-100  p-4 text-black w-64 h-35">
          <Image src="/sand-clock.png" alt="" width={40} height={40} />
          <div>Pending Analysis</div>
          <div className="text-3xl">34</div>
          <div>In queue</div>
        </div>
      </div>
      <div className="pl-12">
        <div className="border text-black border-gray-300 h-20 rounded-md">
          <span className="text-2xl pl-2">Recent Reports</span>
          <span className="pl-100">
            <Link
              href="/update-dashboard"
              className="bg-blue-600 text-white px-3 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition mt-3"
            >
              <div className="flex items-center justify-center">
                <svg
                  className="center"
                  width="20"
                  height="25"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M21 12a9 9 0 1 1-2.64-6.36"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M21 3v6h-6"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              Fetch Dashboard Now
            </Link>
          </span>
        </div>
      </div>
      <div className="flex text-black pl-12 gap-5">
        <div className="border w-97 rounded-md">
          <div className="text-gray-500 border">Recent Reports</div>
          <div className="text-sm text-gray-500">Today 1:00 PM</div>
          <div>Daily Email Summary</div>
          <div className="text-gray-500">
            Fetched 356 emails, analysed 267 by AI
          </div>
        </div>
        <div className="border w-97 rounded-md">
          <div className="text-gray-500 border">Upcoming Schedule</div>
          <div className="text-sm text-gray-500">Today 06:00 PM</div>
          <div>Generate daily email summary</div>
          <div className="text-gray-500">
            Fetched 356 emails, analysed 267 by AI
          </div>
        </div>
      </div>
      <p className="text-black pl-12 pt-2">
        • Al analysis runs continuously. Most emails are processed within 2-5
        minutes.
      </p>
    </div>
  );
};

export default DashboardPage;

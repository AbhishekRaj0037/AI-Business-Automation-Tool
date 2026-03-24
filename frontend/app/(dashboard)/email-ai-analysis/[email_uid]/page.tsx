"use client";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

async function getMail(imap_uid: any, page: any) {
  const res = await fetch(
    `http://localhost:8000/get-reports-by-id?imap_uid=${imap_uid}&page=${page}&limit=4`,
    {
      cache: "no-store",
      credentials: "include",
    },
  );

  if (res.status === 401) {
    window.location.href = "/login";
  }
  if (!res.ok) {
    throw new Error("Failed to fetch data");
  }
  const data = await res.json();
  return data;
}

const DashboardPage = () => {
  const router = useRouter();
  const [email, setEmailData] = useState<any>(null);
  const [page, setPage] = useState(1);
  const params = useParams();
  useEffect(() => {
    async function fetchData() {
      const mail_Data = await getMail(params.email_uid, page);
      setEmailData(mail_Data);
    }
    fetchData();
  }, [page]);

  const [selectedFile, setSelectedFile] = useState(null);
  return (
    <>
      {email && (
        <div>
          <div className="mb-2 mt-4 text-black">
            <div className="border text-black border-gray-300 h-20 rounded-md pt-6">
              <span className="text-2xl pl-4 mt-4">
                {email.mail_result.subject}
              </span>
            </div>
            <div className="border text-black border-gray-300 h-20 rounded-md flex items-center gap-3 px-4">
              <img
                src="https://i.pravatar.cc/40"
                className="w-10 h-10 rounded-full"
                alt="profile"
              />
              <span className="font-semibold m-2">
                <div>{email.mail_from}</div>
              </span>
              <span className="pl-60">
                Received: {email.mail_result.received_at}
              </span>
            </div>
          </div>
          <div className="text-black text-lg border border-black p-4">
            Email Body
          </div>
          <div className="text-black border border-black mb-4">
            <p className="m-4">{email.mail_result.body}</p>
          </div>
          <table className="border border-gray-300 w-full text-left text-black">
            <thead className="bg-gray-100 text-center">
              <tr>
                <th className="border px-4 py-2 text-center">Attachments</th>
                <th className="border px-4 py-2 text-center">File Type</th>
                <th className="border px-4 py-2 text-center">Size</th>
                <th className="border px-4 py-2 text-center">AI Analysis</th>
                <th className="border px-4 py-2 text-center">View</th>
              </tr>
            </thead>
            <tbody>
              {email.attachment_result?.map((file: any, index: any) => {
                const fileUrl = email.list_of_file_presigned_url?.[index];

                return (
                  <tr className="border-t" key={index}>
                    <td className="border px-4 py-2 text-green-600 text-center">
                      {file.file_name}
                    </td>

                    <td className="border px-4 py-2 text-center">
                      {file.file_type?.toUpperCase()}
                    </td>

                    <td className="border px-4 py-2 text-center">
                      {(file.file_size / 1024 / 1024).toFixed(2)} MB
                    </td>

                    <td className="border px-4 py-2 text-center">
                      <a
                        href={`/report/${index}`}
                        className="text-blue-600 hover:underline"
                      >
                        Give it to AI
                      </a>
                    </td>

                    <td className="border px-4 py-2">
                      <div className="flex justify-center items-center h-full">
                        <button
                          onClick={() => {
                            {
                              console.log("File url current===> ", fileUrl);
                            }
                            setSelectedFile(fileUrl);
                          }}
                          className="text-blue-600 hover:underline"
                        >
                          👁
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {selectedFile && (
            <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
              {/* Close button */}
              <button
                onClick={() => setSelectedFile(null)}
                className="absolute top-5 right-5 text-white text-2xl"
              >
                ✖
              </button>

              {/* File Viewer */}
              <div className="bg-white w-[80%] h-[80%] rounded-lg overflow-hidden shadow-lg">
                {/* PDF / general viewer */}
                <iframe src={selectedFile} className="w-full h-full" />
              </div>
            </div>
          )}
          <div className="flex items-center justify-between px-6 py-4 border-t rounded-b-xl text-black">
            {/* Left side */}
            <span className="text-sm text-gray-600"></span>

            {/* Right side Pagination */}
            <div className="flex items-center gap-2">
              <button
                className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100 "
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                Previous
              </button>

              <button
                className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100"
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </div>

          <p className="text-black pt-2">
            • Al analysis runs continuously. Most emails are processed within
            2-5 minutes.
          </p>
        </div>
      )}
    </>
  );
};

export default DashboardPage;

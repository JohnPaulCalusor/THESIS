export default function CsvDownloadButton({ href }: { href: string }) {
  return (
    <a
      href={href}
      className="inline-flex items-center rounded-md bg-blue-600 hover:bg-blue-700 px-4 h-10 font-semibold"
    >
      Download CSV
    </a>
  );
}

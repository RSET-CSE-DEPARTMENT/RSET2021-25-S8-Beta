const BusDataTable = ({ data }) => {
  if (!data || data.length === 0) {
    return <p>No data available</p>;
  }

  return (
    <div>
      {data.map((item, index) => (
        <div key={index}>
          {Object.entries(item).map(([key, value]) => (
            <p key={key} className="text-gray-700">
              <strong>{key.toUpperCase()}:</strong> {value}
            </p>
          ))}
        </div>
      ))}
    </div>
  );
};

export default BusDataTable;

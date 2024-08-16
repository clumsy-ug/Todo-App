import React from "react";

const Spinner: React.FC = () => {
    return (
        <div className="spinner-container">
            <div className="spinner" role="status"></div>
            <div className="spinner-text">Loading...</div>
        </div>
    );
};

export default Spinner;

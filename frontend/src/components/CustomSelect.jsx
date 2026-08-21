import { useState, useEffect, useRef } from "react";

function CustomSelect({
  name,
  value,
  onChange,
  options = [],
  placeholder = "Search or select...",
  disabled = false,
}) {
  // Convert text for display only
  const formatOption = (option) => {
    return String(option)
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const [search, setSearch] = useState(
    value ? formatOption(value) : ""
  );

  const [isOpen, setIsOpen] = useState(false);

  const wrapperRef = useRef(null);

  // Update displayed value when parent value changes
  useEffect(() => {
    setSearch(
      value ? formatOption(value) : ""
    );
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  // Filter options
  const filteredOptions = options.filter((option) =>
    String(option)
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  // Select an option
  const handleSelect = (option) => {
    // Display formatted value
    setSearch(formatOption(option));

    // Send ORIGINAL value to parent/backend
    onChange({
      target: {
        name: name,
        value: String(option),
      },
    });

    setIsOpen(false);
  };

  // Search input
  const handleInputChange = (event) => {
    const inputValue = event.target.value;

    setSearch(inputValue);

    setIsOpen(true);
  };

  return (
    <div
      className="custom-select"
      ref={wrapperRef}
    >
      <div className="custom-select-input-wrapper">

        <input
          className="custom-select-input"
          type="text"
          value={search}
          placeholder={placeholder}
          disabled={disabled}
          autoComplete="off"
          onFocus={() => {
            if (!disabled) {
              setIsOpen(true);
            }
          }}
          onChange={handleInputChange}
        />

        <span className="custom-select-arrow">
          ▾
        </span>

      </div>

      {isOpen && !disabled && (
        <div className="custom-select-dropdown">

          {filteredOptions.length > 0 ? (

            filteredOptions.map((option) => (

              <div
                key={option}
                className="custom-select-option"
                onClick={() =>
                  handleSelect(option)
                }
              >
                {formatOption(option)}
              </div>

            ))

          ) : (

            <div className="custom-select-empty">
              No options found
            </div>

          )}

        </div>
      )}

    </div>
  );
}

export default CustomSelect;
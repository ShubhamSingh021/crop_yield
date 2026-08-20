import { useState, useRef, useEffect } from "react";

function CustomSelect({
  name,
  value,
  onChange,
  options = [],
  placeholder = "Select an option",
  disabled = false,
}) {
  const [isOpen, setIsOpen] = useState(false);

  const selectRef = useRef(null);


  // ============================================
  // FORMAT ONLY FOR DISPLAY
  // JAIPUR -> Jaipur
  // SOUTH ANDAMAN -> South Andaman
  // WEST GODAVARI -> West Godavari
  // ============================================

  const formatDistrictName = (text) => {
    if (!text) return "";

    return text
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };


  // ============================================
  // CLOSE DROPDOWN WHEN CLICKING OUTSIDE
  // ============================================

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        selectRef.current &&
        !selectRef.current.contains(event.target)
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


  // ============================================
  // HANDLE OPTION CLICK
  // ============================================

  const handleSelect = (option) => {
    onChange({
      target: {
        name: name,
        value: option,
      },
    });

    setIsOpen(false);
  };


  // ============================================
  // DISPLAY SELECTED VALUE
  // ============================================

  const displayValue = value
    ? formatDistrictName(value)
    : placeholder;


  return (
    <div
      className={`custom-select ${
        disabled ? "disabled" : ""
      }`}
      ref={selectRef}
    >

      <button
        type="button"
        className="custom-select-trigger"
        disabled={disabled}
        onClick={() => {
          if (!disabled) {
            setIsOpen(!isOpen);
          }
        }}
      >

        <span
          className={
            value
              ? "selected-value"
              : "placeholder-value"
          }
        >
          {displayValue}
        </span>

        <span
          className={`select-arrow ${
            isOpen ? "open" : ""
          }`}
        >
          ▾
        </span>

      </button>


      {isOpen && !disabled && (

        <div className="custom-select-menu">

          {options.length > 0 ? (

            options.map((option) => (

              <button
                type="button"
                key={option}
                className={`custom-select-option ${
                  value === option
                    ? "selected"
                    : ""
                }`}
                onClick={() =>
                  handleSelect(option)
                }
              >

                {formatDistrictName(option)}

              </button>

            ))

          ) : (

            <div className="custom-select-empty">
              No options available
            </div>

          )}

        </div>

      )}

    </div>
  );
}


export default CustomSelect;
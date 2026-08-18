import { useEffect, useRef, useState } from "react";

function CustomSelect({
  name,
  value,
  onChange,
  options = [],
  placeholder = "Select...",
  disabled = false,
}) {

  const [open, setOpen] = useState(false);

  const selectRef = useRef(null);

  useEffect(() => {

    const handleOutsideClick = (event) => {

      if (
        selectRef.current &&
        !selectRef.current.contains(event.target)
      ) {
        setOpen(false);
      }

    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };

  }, []);


  const handleSelect = (option) => {

    onChange({
      target: {
        name,
        value: option,
      },
    });

    setOpen(false);
  };


  return (
    <div
      ref={selectRef}
      className={`custom-select ${
        open ? "custom-select-open" : ""
      } ${disabled ? "custom-select-disabled" : ""}`}
    >

      <button
        type="button"
        className="custom-select-button"
        disabled={disabled}
        onClick={() => {

          if (!disabled) {
            setOpen((previous) => !previous);
          }

        }}
      >

        <span
          className={
            value
              ? "custom-select-value"
              : "custom-select-placeholder"
          }
        >
          {value || placeholder}
        </span>

        <span
          className={`custom-select-arrow ${
            open ? "arrow-up" : ""
          }`}
        >
          ▾
        </span>

      </button>


      {open && !disabled && (

        <div className="custom-select-menu">

          {options.length === 0 ? (

            <div className="custom-select-empty">
              No options available
            </div>

          ) : (

            options.map((option) => (

              <button
                type="button"
                key={option}
                className={`custom-select-option ${
                  value === option
                    ? "custom-select-option-active"
                    : ""
                }`}
                onClick={() =>
                  handleSelect(option)
                }
              >

                <span>
                  {option}
                </span>

                {value === option && (
                  <span>✓</span>
                )}

              </button>

            ))

          )}

        </div>

      )}

    </div>
  );
}

export default CustomSelect;
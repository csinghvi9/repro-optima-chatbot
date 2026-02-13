import { useState, useEffect } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import userInformation from "@/components/user_info/user_info";

type LoanEMIFormProps = {
  newThreadID: string;
  setShowForm: React.Dispatch<React.SetStateAction<boolean>>;
  showForm: boolean;
  setSubmittedForm: React.Dispatch<React.SetStateAction<boolean>>;
  setResponse: React.Dispatch<React.SetStateAction<number>>;
};

export default function LoanEMIForm({
  newThreadID,
  setShowForm,
  showForm,
  setSubmittedForm,
  setResponse,
}: LoanEMIFormProps) {
  const [isChecked, setIsChecked] = useState<boolean>(false);
  const { sendMessage, isConnected } = useWebSocket() as {
    sendMessage: (message: any) => void;
    isConnected: boolean;
  };
  const { updateUserInfo, generateReferenceNumber } = userInformation();
  const [selectedCode, setSelectedCode] = useState("+91");
  const [open, setOpen] = useState(false);
  const countries = [
    { name: "United States", code: "+1" },
    { name: "United Kingdom", code: "+44" },
    { name: "Australia", code: "+61" },
    { name: "Germany", code: "+49" },
    { name: "France", code: "+33" },
    { name: "India", code: "+91" },
  ];
  const [formData, setFormData] = useState({
    firstName: "",
    mobile: "",
    email: "",
    employmentType: "",
    address: "",
    treatmentLocation: "",
    pincode: null,
    state: "",
    pan: "",
    aadhar: null,
  });
  const [formErrors, setFormErrors] = useState<{
    firstName: string;
    mobile: string;
    email: string;
    pincode: string;
    pan: string;
    aadhar: string;
  }>({
    firstName: "",
    mobile: "",
    email: "",
    pincode: "",
    pan: "",
    aadhar: "",
  });

  const handleNumberChange = (field: string, value: string) => {
    setFormData({
      ...formData,
      [field]: value === "" ? null : parseInt(value, 10),
    });
    setFormErrors({ ...formErrors, aadhar: "" });
  };
  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  const handleSend = async () => {
    const errors: any = {};

    // Full Name
    if (!formData.firstName.trim()) {
      errors.firstName = "Full name is required.";
    } else if (!fullNameRegex.test(formData.firstName.trim())) {
      errors.firstName = "Full name can contain only alphabets and spaces.";
    }

    // Mobile
    // Mobile validation
    const mobileParts = formData.mobile.trim().split(" ");

    if (mobileParts.length !== 2) {
      errors.mobile =
        "Mobile number must be 10 digits";
    } else {
      const phoneNumber = mobileParts[1];

      if (!/^[6-9]\d{9}$/.test(phoneNumber)) {
        errors.mobile =
          "Mobile number must be 10 digits and start with 6, 7, 8, or 9.";
      }
    }

    // Email (if provided)
    if (formData.email && !emailRegex.test(formData.email)) {
      errors.email = "Email must be a valid .com email address.";
    }

    // Pincode
    if (formData.pincode && !pincodeRegex.test(String(formData.pincode))) {
      errors.pincode = "Pincode must be exactly 6 digits.";
    }

    // PAN
    if (!panRegex.test(formData.pan.toUpperCase())) {
      errors.pan = "PAN must be in format: ABCDE1234F.";
    }

    // Aadhar
    if (!aadharRegex.test(String(formData.aadhar))) {
      errors.aadhar = "Aadhar number must be exactly 12 digits.";
    }

    // ❌ If any errors → stop
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    // ✅ Clear errors
    setFormErrors({
      firstName: "",
      mobile: "",
      email: "",
      pincode: "",
      pan: "",
      aadhar: "",
    });

    if (isConnected) {
      const response = await updateUserInfo(newThreadID, formData);
      if (response?.status === 200) {
        setShowForm(false);
        setSubmittedForm(true);
        setResponse(response?.data?.reference_id);
      }
    }
  };

  const mobileRegex = /^[6-9]\d{9}$/;
  const emailRegex = /^[^\s@]+@[^\s@]+\.com$/i;
  const pincodeRegex = /^\d{6}$/;
  const aadharRegex = /^\d{12}$/;
  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
  const fullNameRegex = /^[A-Za-z]+(?: [A-Za-z]+)*$/;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="relative bg-white shadow-lg border border-gray-300 w-[90%] md:w-[60vw] md:h-[60vh] h-[90%] rounded-2xl flex flex-col p-6">
        <div className="flex flex-row justify-between items-center">
          <span className="text-[18px] md:text-[28px] font-indira_font text-indira_text font-semibold">
            Please fill in the details
          </span>
          <button
            onClick={() => setShowForm(false)}
            className="text-gray-500 hover:text-gray-700 cursor-pointer"
          >
            <img src="/close_cross.svg" alt="close" className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-y-auto customScrollbar pr-2 flex-1 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-4 md:gap-y-2">
            {/* Example Input Fields */}
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Full Name <span className="text-[#E5000B]">*</span>
              </label>

              <input
                type="text"
                required
                placeholder="Enter your name"
                className={`mt-1 block w-full rounded-lg border px-3 py-2 text-sm text-indira_text focus:outline-none placeholder:indira_input_label_text ${
                  formErrors.firstName
                    ? "border-red-500"
                    : "border-indira_input_label_text"
                }`}
                onChange={(e) => {
                  setFormData({ ...formData, firstName: e.target.value });
                  setFormErrors({ ...formErrors, firstName: "" });
                }}
              />

              {formErrors.firstName && (
                <p className="text-red-500 text-xs mt-0.5">
                  {formErrors.firstName}
                </p>
              )}
            </div>

            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Mobile Number <span className="text-[#E5000B]">*</span>
              </label>
              <div className="relative mt-1">
                {/* Dropdown Trigger */}
                <button
                  type="button"
                  className="absolute inset-y-0 left-0 flex items-center pl-2 pr-2 text-sm text-indira_text border-r border-indira_input_label_text focus:outline-none cursor-pointer"
                  onClick={() => setOpen(!open)}
                >
                  {selectedCode}
                  <img
                    src="./dropdown_arrow.svg"
                    className="w-[10px] h-[10px] ml-[2px]"
                  />
                </button>

                {/* Input */}
                <input
                  type="text"
                  required
                  placeholder="Enter your mobile number"
                  className="text-indira_text block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:text-indira_input_label_text pl-16"
                  value={formData.mobile.replace(selectedCode, "")} // only show number
                  onChange={(e) => {
                    const numberOnly = e.target.value
                      .replace(/\D/g, "")
                      .slice(0, 10);

                    setFormData({
                      ...formData,
                      mobile: `${selectedCode} ${numberOnly}`,
                    });

                    setFormErrors({ ...formErrors, mobile: "" });
                  }}
                />

                {/* Dropdown Menu */}
                {open && (
                  <div className="absolute z-10 mt-1 bg-white border border-indira_input_label_text rounded-lg shadow w-60 max-h-40 overflow-y-auto customScrollbar">
                    <ul className="py-1 text-sm text-indira_text">
                      {countries.map((c) => (
                        <li key={c.code}>
                          <button
                            type="button"
                            className="w-full px-4 py-2 text-left hover:bg-gray-100 cursor-pointer"
                            onClick={() => {
                              const numberOnly = formData.mobile.replace(
                                selectedCode,
                                "",
                              ); // remove old code
                              setSelectedCode(c.code);
                              setFormData({
                                ...formData,
                                mobile: `${c.code}${numberOnly}`, // add new code once
                              });
                              setOpen(false);
                            }}
                          >
                            {c.code} – {c.name}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              {formErrors.mobile && (
                <p className="text-red-500 text-[10px] mt-0.5">
                  {formErrors.mobile}
                </p>
              )}
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Email ID
              </label>
              <input
                type="email"
                placeholder="Enter email"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
              {formErrors.email && (
                <p className="text-red-500 text-xs mt-0.5">
                  {formErrors.email}
                </p>
              )}
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Employment Type
              </label>

              <div className="relative mt-1 ">
                <select
                  name="employmentType"
                  id="employmentType"
                  className="text-indira_text block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none focus:border-indira_hello_border placeholder:indira_input_label_text focus:ring-indira_input_label_text focus:ring-1 appearance-none  customScrollbar "
                  value={formData.employmentType}
                  onChange={(e) =>
                    setFormData({ ...formData, employmentType: e.target.value })
                  }
                >
                  <option value="">Select Type</option>
                  <option value="Salaried">Salaried</option>
                  <option value="Self-Employed">Self-Employed</option>
                  <option value="Buisness Owner">Buisness Owner</option>
                  <option value="Homemaker">Homemaker</option>
                  <option value="Unemployed">Unemployed</option>
                  <option value="Retired">Retired</option>
                  <option value="Government Employee">
                    Government Employee
                  </option>
                  <option value="Other">Other</option>
                </select>

                {/* Arrow inside input */}
                <img
                  src="./dropdown_arrow.svg"
                  className="absolute inset-y-0 right-3 flex items-center pointer-events-none mt-[15px]"
                />
              </div>
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Address
              </label>
              <input
                type="text"
                placeholder="Enter address"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.address}
                onChange={(e) =>
                  setFormData({ ...formData, address: e.target.value })
                }
              />
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Treatment Location
              </label>
              <input
                type="text"
                placeholder="Enter location"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.treatmentLocation}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    treatmentLocation: e.target.value,
                  })
                }
              />
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Pincode
              </label>
              <input
                type="number"
                placeholder="Enter pincode"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.pincode ?? ""} // show empty string if null
                onChange={(e) => handleNumberChange("pincode", e.target.value)}
              />
              {formErrors.pincode && (
                <p className="text-red-500 text-xs mt-0.5">
                  {formErrors.pincode}
                </p>
              )}
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                State
              </label>
              <div className="relative mt-1">
                <select
                  className="text-indira_text block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text appearance-none pr-8 customScrollbar"
                  value={formData.state || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, state: e.target.value })
                  }
                >
                  <option value="" disabled>
                    Select state
                  </option>
                  <option value="andhra-pradesh">Andhra Pradesh</option>
                  <option value="arunachal-pradesh">Arunachal Pradesh</option>
                  <option value="assam">Assam</option>
                  <option value="bihar">Bihar</option>
                  <option value="chhattisgarh">Chhattisgarh</option>
                  <option value="goa">Goa</option>
                  <option value="gujarat">Gujarat</option>
                  <option value="haryana">Haryana</option>
                  <option value="himachal-pradesh">Himachal Pradesh</option>
                  <option value="jharkhand">Jharkhand</option>
                  <option value="karnataka">Karnataka</option>
                  <option value="kerala">Kerala</option>
                  <option value="madhya-pradesh">Madhya Pradesh</option>
                  <option value="maharashtra">Maharashtra</option>
                  <option value="manipur">Manipur</option>
                  <option value="meghalaya">Meghalaya</option>
                  <option value="mizoram">Mizoram</option>
                  <option value="nagaland">Nagaland</option>
                  <option value="odisha">Odisha</option>
                  <option value="punjab">Punjab</option>
                  <option value="rajasthan">Rajasthan</option>
                  <option value="sikkim">Sikkim</option>
                  <option value="tamil-nadu">Tamil Nadu</option>
                  <option value="telangana">Telangana</option>
                  <option value="tripura">Tripura</option>
                  <option value="uttar-pradesh">Uttar Pradesh</option>
                  <option value="uttarakhand">Uttarakhand</option>
                  <option value="west-bengal">West Bengal</option>
                </select>

                {/* Custom Arrow */}
                <img
                  src="./dropdown_arrow.svg"
                  className="absolute inset-y-0 right-3 my-auto pointer-events-none"
                />
              </div>
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                PAN Card Number<span className="text-[#E5000B]">*</span>
              </label>
              <input
                type="text"
                required
                placeholder="Enter PAN"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.pan}
                onChange={(e) => {
                  setFormData({
                    ...formData,
                    pan: e.target.value.toUpperCase(),
                  });
                  setFormErrors({ ...formErrors, pan: "" });
                }}
              />
              {formErrors.pan && (
                <p className="text-red-500 text-xs mt-0.5">{formErrors.pan}</p>
              )}
            </div>
            <div className="h-18">
              <label className="block text-sm font-medium text-indira_text">
                Aadhar Number<span className="text-[#E5000B]">*</span>
              </label>
              <input
                type="number"
                required
                placeholder="Enter Aadhar"
                className="text-indira_text mt-1 block w-full rounded-lg border border-indira_input_label_text px-3 py-2 text-sm focus:outline-none placeholder:indira_input_label_text"
                value={formData.aadhar ?? ""} // show empty string if null
                onChange={(e) => {
                  handleNumberChange("aadhar", e.target.value);
                }}
              />
              {formErrors.aadhar && (
                <p className="text-red-500 text-xs mt-0.5">
                  {formErrors.aadhar}
                </p>
              )}
            </div>
          </div>
          <div className="flex flex-row mt-4">
            <label className="flex items-center gap-2 cursor-pointer">
              {/* Checkbox + Icon Wrapper */}
              <div className="relative">
                {/* Checkbox */}
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) => setIsChecked(e.target.checked)}
                  className="peer appearance-none w-5 h-5 border border-gray-400 rounded-md checked:bg-[#4DBB3E] checked:border-transparent flex items-center justify-center"
                />
                {/* Checkmark Icon */}
                <svg
                  className="hidden peer-checked:block absolute inset-0 m-auto w-3 h-3 text-white pointer-events-none "
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={3}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>

              {/* Text */}
              <span className="text-[16px] text-[#717272]">
                By clicking submit; You agree to our{" "}
                <a
                  href="https://meddilink.com/privacy-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline"
                >
                  privacy policy
                </a>{" "}
                and{" "}
                <a
                  href="https://meddilink.com/terms-and-conditions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline"
                >
                  T&amp;C
                </a>
              </span>
            </label>
          </div>
          <button
            disabled={!isChecked} // optional if you want it clickable only when checked
            className={`w-full rounded-[999px] mt-5 h-[54px] text-[20px] transition-colors cursor-pointer ${
              isChecked
                ? "bg-gradient-to-br from-[#F04F5F] to-[#CE3149] text-white hover:opacity-90"
                : "bg-[#F2F2F2] text-[#D9D9D9] cursor-not-allowed"
            }`}
            onClick={handleSend}
          >
            Submit
          </button>
          {/* <button
                                disabled={!isChecked} // optional if you want it clickable only when checked
                                className={`w-full rounded-[999px] mt-5 h-[54px] text-[20px] transition-colors ${isChecked
                                    ? "bg-gradient-to-br from-[#F04F5F] to-[#CE3149] text-white hover:opacity-90"
                                    : "bg-[#F2F2F2] text-[#D9D9D9] cursor-not-allowed"
                                    }`}
                                onClick={() =>setSubmittedForm(true)}
                            >
                                check
                            </button> */}
          <div className="flex items-center justify-center">
            <img src="./secure.svg" className="mt-4 mr-2" />
            <span className="text-[16px] text-indira_text mt-4 justify-between">
              Your data is safe with us
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

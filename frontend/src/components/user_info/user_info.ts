import axios from "axios";

interface UserFormData {
  firstName: string;
  mobile: string;
  email: string;
  employmentType: string;
  address: string;
  treatmentLocation: string;
  pincode: number | null;
  state: string;
  pan: string;
  aadhar: number | null;
}

export default function userInformation() {
  const updateUserInfo = async (thread_id: string, formData: UserFormData) => {
    try {
      const mappedData = {
        name: formData.firstName,
        phone_number: formData.mobile,
        email_id: formData.email,
        pincode: formData.pincode, // ensure string
        user_address: formData.address,
        employment_type: formData.employmentType,
        state: formData.state,
        treatment_location: formData.treatmentLocation,
        pan_number: formData.pan,
        aadhar_number: formData.aadhar,
      };
      const token = sessionStorage.getItem("guest_token");

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/loan_user/insert_loan_user_info?thread_id=${thread_id}`,
        mappedData,
        {
          headers: {
            Authorization: `${token || ""}`,
            "Content-Type": "application/json",
          },
        }
      );
      // return response.status

      return response;
    } catch (error) {
      console.error("Failed to send user info:", error);
      return null;
    }
  };
  const generateReferenceNumber = async () => {
    try {
      const token = sessionStorage.getItem("guest_token");

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user_info/generate_reference_number`,
        {
          headers: {
            Authorization: `${token || ""}`,
            "Content-Type": "application/json",
          },
        }
      );
      // return response.status

      return response.data.reference_number;
    } catch (error) {
      console.error("Failed to send user info:", error);
      return null;
    }
  };

  return {
    updateUserInfo,
    generateReferenceNumber,
  };
}

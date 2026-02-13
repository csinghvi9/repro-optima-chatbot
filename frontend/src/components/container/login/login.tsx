import React, { useState } from "react";
import admin from "@/components/admin_auth/auth"; 
import Dashboard from "@/components/container/dashboard/dashboard"

const Login: React.FC = () => {
    const { adminLogin } = admin();
    const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [validUser,isvalidUser]=useState<boolean>(false);
   const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await adminLogin(formData);

    if (res && res.data?.token) {
      // ✅ Save token for later authenticated requests
      sessionStorage.setItem("admin_access_token", res?.data?.token?.access_token);
      sessionStorage.setItem("admin_refresh_token", res?.data?.token?.refresh_token);
      isvalidUser(true);
      // redirect if needed:
      // router.push("/dashboard");
    } else  {
      alert("Invalid email or password");
    }
  };
    if (validUser) {
    return <Dashboard />;
  }
  return (
    <section className="bg-[#FFF4F8] h-screen">
  <div className="flex flex-col items-center justify-center px-6 py-8 mx-auto h-screen lg:py-0 font-indira_font">
      {/* <a href="#" className="flex items-center mb-6 text-2xl font-semibold text-gray-900 dark:text-white">
          <img className="w-8 h-8 mr-2" src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg" alt="logo" />
          Flowbite    
      </a> */}
      <div className="w-full border border-indira_border  rounded-lg shadow  md:mt-0 sm:max-w-md xl:p-0 bg-[#FBF8FF]">
          <div className="p-6 space-y-4 md:space-y-6 sm:p-8">
              <h1 className="text-xl font-semibold font-indira_font text-indira_text md:text-2xl ">
                  Sign in to your account
              </h1>
              <form className="space-y-4 md:space-y-6" action="#">
                  <div>
                      <label  className="block mb-2 text-sm font-medium text-indira_text">Email</label>
                      <input type="email" name="email" id="email" className="bg-[#FFFFFF] border border-indira_hello_border text-indira_hover_text rounded-lg block w-full p-2.5 placeholder:text-indira_input_label_text focus:outline-none" placeholder="name@company.com"
                      value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })} required  />
                  </div>
                  <div>
                      <label  className="block mb-2 text-sm font-medium text-indira_text">Password</label>
                      <input type="password" name="password" id="password" placeholder="********" className="bg-[#FFFFFF] border border-indira_hello_border text-indira_hover_text rounded-lg block w-full p-2.5 placeholder:text-indira_input_label_text focus:outline-none"  
                      value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  />
                  </div>
                  {/* <div className="flex items-center justify-between">
                      <div className="flex items-start">
                          <div className="flex items-center h-5">
                            <input id="remember" aria-describedby="remember" type="checkbox" className="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 dark:ring-offset-gray-800" />
                          </div>
                          <div className="ml-3 text-sm">
                            <label  className="text-gray-500 dark:text-gray-300">Remember me</label>
                          </div>
                      </div>
                      <a href="#" className="text-sm font-medium text-primary-600 hover:underline dark:text-primary-500">Forgot password?</a>
                  </div> */}
                            <button className="w-full rounded-[999px] mt-5 h-[54px] text-[20px] transition-colors cursor-pointer bg-gradient-to-br from-[#F04F5F] to-[#CE3149] text-white hover:opacity-90" onClick={handleSubmit}
      
            

          >
            Log In
          </button>
                  {/* <p className="text-sm font-light text-gray-500 dark:text-gray-400">
                      Don’t have an account yet? <a href="#" className="font-medium text-primary-600 hover:underline dark:text-primary-500">Sign up</a>
                  </p> */}
              </form>
          </div>
      </div>

  </div>
</section>

  );
};

export default Login;

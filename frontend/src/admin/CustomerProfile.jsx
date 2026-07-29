import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getApiUrl } from "../utils/api";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

import "./CustomerProfile.css";


export default function CustomerProfile(){

    const { id } = useParams();

    const [customer,setCustomer] = useState(null);
    const [loading,setLoading] = useState(true);



    useEffect(()=>{

        loadCustomer();

    },[]);



    async function loadCustomer(){

        try{

            const response = await fetch(
                `http://127.0.0.1:5000/api/admin/customers/${id}`
            );


            const data = await response.json();


            if(response.ok){

                setCustomer(data);

            }
            else{

                console.log(data);

            }


        }
        catch(error){

            console.log(
                "Customer loading error:",
                error
            );

        }
        finally{

            setLoading(false);

        }

    }





    if(loading){

        return (

            <h2>
                Loading customer...
            </h2>

        );

    }




    if(!customer){

        return (

            <h2>
                Customer not found
            </h2>

        );

    }





    return (

        <div className="admin-layout">


            <Sidebar/>


            <div className="main-content">


                <Topbar/>




                <div className="profile-header">

                    <h1>
                        {customer.name}
                    </h1>


                    <p>
                        Customer Profile
                    </p>


                </div>







                <div className="profile-grid">





                    <div className="profile-card">


                        <h2>
                            Personal Information
                        </h2>



                        <p>
                            Email:
                            {" "}
                            {customer.email}
                        </p>



                        <p>
                            Phone:
                            {" "}
                            {customer.phone || "N/A"}
                        </p>



                        <p>
                            Address:
                            {" "}
                            {customer.address || "N/A"}
                        </p>



                        <p>
                            Status:
                            {" "}
                            {customer.status}
                        </p>



                    </div>








                    <div className="profile-card">


                        <h2>
                            Account Information
                        </h2>





                        <p>
                            Account Number:
                            {" "}
                            {customer.account?.account_number || "N/A"}
                        </p>





                        <p>
                            Account Type:
                            {" "}
                            {customer.account?.account_type || "N/A"}
                        </p>





                        <p>
                            Balance:
                            {" "}
                            $
                            {Number(
                                customer.account?.balance || 0
                            ).toLocaleString()}
                        </p>





                        <p>
                            Currency:
                            {" "}
                            {customer.account?.currency || "USD"}
                        </p>



                    </div>






                </div>





            </div>



        </div>

    );


}
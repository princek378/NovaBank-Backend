import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { getApiUrl } from "../utils/api";

import "./Sidebar.css";



export default function Sidebar(){


    const [bankName,setBankName] = useState(
        "NovaBank"
    );





    useEffect(()=>{


        loadSettings();


    },[]);






    async function loadSettings(){


        try{


            const response = await fetch(

                `${getApiUrl()}/api/settings`

            );


            const data = await response.json();



            setBankName(

                data.bank_name ||
                "NovaBank"

            );


        }


        catch(error){


            console.log(error);


        }


    }








    return(


        <div className="sidebar">





            <div>



                <div className="logo">


                    <h2>

                        {bankName}

                    </h2>



                    <p>

                        Admin Panel

                    </p>


                </div>







                <nav>


                    <NavLink
    to="/admin/dashboard"
    className="nav-link"
>
    🏠 Dashboard
</NavLink>




                    <NavLink
                        to="/admin/customers"
                        className="nav-link"
                    >

                        👥 Customers

                    </NavLink>





                    <NavLink
                        to="/admin/transactions"
                        className="nav-link"
                    >

                        💳 Transactions

                    </NavLink>





                    <NavLink
                        to="/admin/reports"
                        className="nav-link"
                    >

                        📊 Reports

                    </NavLink>





                    <NavLink
                        to="/admin/messages"
                        className="nav-link"
                    >

                        💬 Messages

                    </NavLink>





                    <NavLink
                        to="/admin/settings"
                        className="nav-link"
                    >

                        ⚙️ Settings

                    </NavLink>



                </nav>


            </div>






            <div className="logout-section">


                <button
                    className="logout-btn"
                    onClick={() => {
                        localStorage.clear();
                        window.location.href = "/";
                    }}
                >
                    🚪 Logout
                </button>


            </div>





        </div>


    );


}
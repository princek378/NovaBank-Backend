import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApiUrl } from "../utils/api";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import StatCard from "../components/StatCard";

import "./AdminDashboard.css";



export default function AdminDashboard(){
	const navigate = useNavigate();


    const [stats,setStats] = useState({

        customers:0,

        accounts:0,

        transactions:0,

        balance:0,

        messages:0

    });



    const [settings,setSettings] = useState({

        bank_name:"NovaBank",

        admin_name:"Administrator"

    });



    const [loading,setLoading] = useState(true);





    useEffect(()=>{


        loadDashboard();


        loadSettings();


    },[]);







    async function loadDashboard(){


        try{


            const response = await fetch(

                `${getApiUrl()}/api/admin/stats`

            );


            const data = await response.json();


            setStats(data);



        }


        catch(error){


            console.log(error);


        }


        finally{


            setLoading(false);


        }


    }








    async function loadSettings(){


        try{


            const response = await fetch(

                `${getApiUrl()}/api/settings`

            );


            const data = await response.json();


            setSettings({

                bank_name:
                data.bank_name ||
                "NovaBank",


                admin_name:
                data.admin_name ||
                "Administrator"

            });


        }


        catch(error){


            console.log(error);


        }


    }









    return(


        <div className="admin-layout">


            <Sidebar/>




            <div className="main-content">


                <Topbar/>





                <div className="dashboard-title">


                    <h1>

                        {settings.bank_name}
                        {" "}
                        Admin Dashboard

                    </h1>





                    <p>

                        Welcome back,
                        {" "}
                        {settings.admin_name}.
                        Manage your bank operations from here.

                    </p>


                </div>







                {

                loading ?


                <div className="loading-box">

                    Loading dashboard data...

                </div>



                :



                <div className="cards">





                    <StatCard

                        title="Total Customers"

                        value={stats.customers}

                        icon="👥"

                    />





                    <StatCard

                        title="Total Accounts"

                        value={stats.accounts}

                        icon="💳"

                    />





                    <StatCard

                        title="Transactions"

                        value={stats.transactions}

                        icon="💸"

                    />





                    <StatCard

                        title="Bank Balance"

                        value={`$${Number(stats.balance).toLocaleString()}`}

                        icon="🏦"

                    />




                </div>


                }








                <div className="admin-section">



                    <h2>

                        Quick Actions

                    </h2>





                    <div className="admin-buttons">



                      <div className="admin-buttons">

    <button
        onClick={() => {
            console.log("Create Customer");
            navigate("/admin/new-customer");
        }}
    >
        ➕ Create Customer
    </button>

    <button
        onClick={() => {
            console.log("Open Live Chat");
            navigate("/admin/messages");
        }}
    >
        💬 Open Live Chat
    </button>

    <button
        onClick={() => {
            console.log("View Reports");
            navigate("/admin/reports");
        }}
    >
        📊 View Reports
    </button>

</div>



                    </div>



                </div>








                <div className="admin-section">


                    <h2>

                        Bank Overview

                    </h2>





                    <div className="overview-grid">





                        <div className="overview-card">


                            <h3>

                                System Status

                            </h3>



                            <p className="online">

                                ● Online

                            </p>


                        </div>







                        <div className="overview-card">


                            <h3>

                                Security

                            </h3>



                            <p>

                                Protected

                            </p>


                        </div>








                        <div className="overview-card">


                            <h3>

                                Support Messages

                            </h3>



                            <p>

                                {stats.messages}

                            </p>


                        </div>





                    </div>



                </div>







            </div>


        </div>


    );


}
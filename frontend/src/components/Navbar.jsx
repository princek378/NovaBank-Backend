import {motion} from "framer-motion";
import { Menu } from "lucide-react";


export default function Navbar(){

return(

<motion.nav

initial={{y:-50,opacity:0}}

animate={{y:0,opacity:1}}

className="navbar"


>


<div className="logo">

Nova<span>Bank</span>

</div>



<div className="links">

<a href="#">Home</a>

<a href="#">Services</a>

<a href="#">Security</a>

<a href="#">Contact</a>

</div>



<div className="nav-actions">


<button className="login-btn">

Login

</button>


<button className="create-btn">

Create Account

</button>


</div>


<Menu className="mobile-menu"/>


</motion.nav>

)

}
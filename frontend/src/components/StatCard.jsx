export default function StatCard({title,value,icon}){


return(

<div className="stat-card">


<div className="stat-icon">

{icon}

</div>


<div className="stat-content">

<h3>
{title}
</h3>


<h1>
{value}
</h1>

</div>


</div>

)


}
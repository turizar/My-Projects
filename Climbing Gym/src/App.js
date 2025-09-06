import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Menu, ClimbingBox, Phone } from "lucide-react";

// Header component
const Header = () => {
  return (
    <header className="bg-gray-900 text-white p-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold">ClimbUp</h1>
      <Menu className="w-6 h-6" />
    </header>
  );
};

// Hero component
const Hero = () => {
  return (
    <section className="bg-[url('/hero.jpg')] bg-cover bg-center text-white h-[60vh] flex flex-col justify-center items-center text-center p-4">
      <h2 className="text-4xl md:text-5xl font-bold mb-4">Discover the Joy of Climbing</h2>
      <p className="mb-6 text-lg md:text-xl">Bouldering for all levels in a fun and safe environment.</p>
      <Button className="bg-green-500 hover:bg-green-600">Book Your First Session</Button>
    </section>
  );
};

// About section
const About = () => {
  return (
    <section className="p-6 max-w-4xl mx-auto">
      <h3 className="text-3xl font-semibold mb-4">About Us</h3>
      <p className="text-gray-700 text-lg">
        Our climbing gym offers top-notch bouldering walls, expert instruction, and a supportive community. Whether you're a beginner or a pro, you'll find challenges, friends, and fun at ClimbUp.
      </p>
    </section>
  );
};

// Services section with dynamic content using useState
const Services = () => {
  const [services, setServices] = useState([
    {
      title: "Bouldering Walls",
      description: "Over 100 problems for all skill levels. New routes every week.",
      icon: <ClimbingBox className="w-10 h-10 mb-4" />,
    },
    {
      title: "Coaching",
      description: "Group and personal training to help you climb better and safer.",
      icon: <Phone className="w-10 h-10 mb-4" />,
    },
    {
      title: "Events",
      description: "Competitions, social nights, and more. Join our vibrant climbing community!",
      icon: <ClimbingBox className="w-10 h-10 mb-4" />,
    },
  ]);

  return (
    <section className="bg-gray-100 p-6">
      <h3 className="text-3xl font-semibold text-center mb-8">What We Offer</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {services.map((service, index) => (
          <Card key={index}>
            <CardContent className="flex flex-col items-center p-6">
              {service.icon}
              <h4 className="text-xl font-bold mb-2">{service.title}</h4>
              <p className="text-gray-600 text-center">{service.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
};

// Contact section with useEffect example
const Contact = () => {
  const [contacted, setContacted] = useState(false);

  useEffect(() => {
    if (contacted) {
      console.log("User clicked on contact info.");
    }
  }, [contacted]);

  return (
    <section className="p-6 max-w-3xl mx-auto">
      <h3 className="text-3xl font-semibold mb-4">Get in Touch</h3>
      <p className="text-gray-700 mb-4">Have questions? Want to book a class? Call us or send a message.</p>
      <div className="flex flex-col gap-2">
        <p onClick={() => setContacted(true)} className="cursor-pointer"><strong>Phone:</strong> +56 9 1234 5678</p>
        <p onClick={() => setContacted(true)} className="cursor-pointer"><strong>Email:</strong> info@climbup.cl</p>
        <p><strong>Address:</strong> Calle Ficticia 123, Santiago, Chile</p>
      </div>
    </section>
  );
};

// Footer component
const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white p-4 text-center mt-10">
      <p>&copy; 2025 ClimbUp. All rights reserved.</p>
    </footer>
  );
};

// Main App Component combining all parts
const App = () => {
  return (
    <div className="font-sans">
      <Header />
      <Hero />
      <About />
      <Services />
      <Contact />
      <Footer />
    </div>
  );
};

export default App;

/*
-- Code Explanation (English) --
1. We've broken the page into reusable components: Header, Hero, About, Services, Contact, and Footer.
2. useState is used to manage a list of services and a boolean flag for contact click.
3. useEffect logs a message to the console when a user clicks on contact information.
4. Components are cleanly separated, which helps keep the code modular and easier to maintain.
5. All UI is styled with Tailwind CSS.
*/

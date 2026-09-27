// LandingPage.jsx — Public landing page assembling all sections.
// Clicking any CTA switches the parent App view to 'booking'.

import LandingHeader from '../components/LandingHeader';
import HeroSection from '../components/HeroSection';
import CourseSection from '../components/CourseSection';
import HowItWorks from '../components/HowItWorks';
import FeaturesSection from '../components/FeaturesSection';
import Testimonials from '../components/Testimonials';
import FAQ from '../components/FAQ';
import CTASection from '../components/CTASection';
import LandingFooter from '../components/LandingFooter';

function LandingPage({ onBookTrial, onViewChange }) {
  const scrollToCourses = () => {
    const el = document.getElementById('courses');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="landing-page">
      <LandingHeader onBookTrial={onBookTrial} onViewChange={onViewChange} />

      <main id="main-content">
        <HeroSection onBookTrial={onBookTrial} onExploreCourses={scrollToCourses} />
        <CourseSection onBookTrial={onBookTrial} />
        <HowItWorks />
        <FeaturesSection />
        <Testimonials />
        <FAQ />
        <CTASection onBookTrial={onBookTrial} />
      </main>

      <LandingFooter onBookTrial={onBookTrial} />
    </div>
  );
}

export default LandingPage;

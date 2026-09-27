// CTASection.jsx — Final call-to-action band above the footer.

function CTASection({ onBookTrial }) {
  return (
    <section className="cta-section" aria-labelledby="cta-heading">
      <div className="cta-inner">
        <h2 className="cta-heading" id="cta-heading">
          Ready to explore your child's next learning experience?
        </h2>
        <p className="cta-subheading">
          Book a free 1-on-1 trial class today. No credit card required.
        </p>
        <button
          type="button"
          className="cta-book-btn"
          onClick={() => onBookTrial()}
          id="cta-book-trial-btn"
        >
          Book a Free Trial →
        </button>
      </div>
    </section>
  );
}

export default CTASection;

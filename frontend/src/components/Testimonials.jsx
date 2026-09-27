// Testimonials.jsx — Sample parent testimonials.
// IMPORTANT: These are clearly fictional/sample testimonials for demonstration purposes only.
// They are not real customer reviews or endorsements.

const TESTIMONIALS = [
  {
    id: 't1',
    quote:
      'Booking the trial was surprisingly smooth. I selected a time that worked for us and received the classroom link immediately after confirming. The whole process took under five minutes.',
    name: 'Priya M.',
    role: 'Parent of a 9-year-old',
    initial: 'P',
  },
  {
    id: 't2',
    quote:
      'I appreciated that the system automatically handled the timezone difference for us — we are based in London. The mentor was prepared and the class felt genuinely personalised.',
    name: 'James R.',
    role: 'Parent of a 12-year-old',
    initial: 'J',
  },
  {
    id: 't3',
    quote:
      'My daughter was hesitant about online learning, but the 1-on-1 structure made it feel much less intimidating than a group class. The booking experience itself was very straightforward.',
    name: 'Anjali S.',
    role: 'Parent of an 11-year-old',
    initial: 'A',
  },
  {
    id: 't4',
    quote:
      'I liked that no account or payment was required just to try the trial class. The mentor assignment happened instantly and the confirmation details were clear.',
    name: 'David K.',
    role: 'Parent of a 10-year-old',
    initial: 'D',
  },
];

function Testimonials() {
  return (
    <section
      className="landing-section testimonials-section"
      id="testimonials"
      aria-labelledby="testimonials-heading"
    >
      <div className="landing-container">
        <div className="section-label-row">
          <span className="section-label-pill">Parent Experiences</span>
        </div>
        <h2 className="landing-section-heading" id="testimonials-heading">
          What Parents Say
        </h2>
        <p className="landing-section-subheading">
          The following are sample testimonials created for demonstration purposes.
          They are not real customer reviews.
        </p>

        <div className="testimonials-grid">
          {TESTIMONIALS.map((t) => (
            <blockquote className="testimonial-card" key={t.id} cite="#">
              <div className="testimonial-quote-mark" aria-hidden="true">"</div>
              <p className="testimonial-text">{t.quote}</p>
              <footer className="testimonial-footer">
                <div className="testimonial-avatar" aria-hidden="true">
                  {t.initial}
                </div>
                <div className="testimonial-author">
                  <cite className="author-name">{t.name}</cite>
                  <span className="author-role">{t.role}</span>
                </div>
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Testimonials;

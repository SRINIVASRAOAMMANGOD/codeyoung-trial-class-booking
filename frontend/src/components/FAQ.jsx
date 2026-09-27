// FAQ.jsx — Accordion FAQ. Answers accurately reflect the actual implemented system.

import { useState } from 'react';

const FAQ_ITEMS = [
  {
    id: 'faq-how-trial-works',
    question: 'How does the free trial class work?',
    answer:
      'Browse available time slots for any date in the next 7 days, fill in your details, and confirm. The system instantly assigns an available mentor and generates a private classroom meeting link. No payment or account creation is required to book a trial class.',
  },
  {
    id: 'faq-duration',
    question: 'How long is a trial class?',
    answer:
      'Trial slots are currently configured as one-hour booking windows, available between 3:00 PM and 9:00 PM India Standard Time (IST). This reflects the current scheduling configuration of the system.',
  },
  {
    id: 'faq-mentor-assignment',
    question: 'How is a mentor assigned?',
    answer:
      'The system automatically identifies an available mentor for your chosen time slot. Eligibility rules ensure each mentor can conduct a maximum of 2 confirmed sessions per calendar day in their local timezone. The first qualifying available mentor is assigned instantly — you do not need to choose manually.',
  },
  {
    id: 'faq-timezones',
    question: 'Can I choose a convenient time from my timezone?',
    answer:
      'Yes. The booking form automatically detects your local timezone and lets you select from a curated list of IANA timezones. All available slots are displayed in your chosen local time, taking Daylight Saving Time (DST) into account correctly.',
  },
  {
    id: 'faq-timezone-storage',
    question: 'What timezone will I see when viewing my booking?',
    answer:
      'Available times are displayed in the timezone you selected when booking. The system stores the booking internally in UTC (Coordinated Universal Time) to eliminate ambiguity, but your confirmation will show the equivalent local time in your selected timezone.',
  },
  {
    id: 'faq-class-link',
    question: 'How will I receive the class link?',
    answer:
      'Your classroom meeting link is displayed immediately on the booking confirmation screen. You can copy it directly from there. In a production deployment, the link would also be delivered by email — the notification architecture supports this and a console-mode email simulation is active during development.',
  },
  {
    id: 'faq-no-mentor',
    question: 'What happens if no mentor is available?',
    answer:
      'If all available mentors are fully booked for your chosen slot, the system returns a clear message indicating no slots are available and prompts you to choose a different date or time. No booking is created in this case.',
  },
];

function FAQItem({ item, isOpen, onToggle }) {
  return (
    <div className={`faq-item ${isOpen ? 'faq-item-open' : ''}`}>
      <button
        type="button"
        className="faq-question"
        aria-expanded={isOpen}
        aria-controls={`${item.id}-answer`}
        id={`${item.id}-btn`}
        onClick={onToggle}
      >
        <span className="faq-q-text">{item.question}</span>
        <span className="faq-chevron" aria-hidden="true">
          {isOpen ? '−' : '+'}
        </span>
      </button>
      {isOpen && (
        <div
          className="faq-answer"
          id={`${item.id}-answer`}
          role="region"
          aria-labelledby={`${item.id}-btn`}
        >
          <p>{item.answer}</p>
        </div>
      )}
    </div>
  );
}

function FAQ() {
  const [openId, setOpenId] = useState(FAQ_ITEMS[0].id);

  const toggle = (id) => {
    setOpenId((current) => (current === id ? null : id));
  };

  return (
    <section
      className="landing-section faq-section"
      id="faq"
      aria-labelledby="faq-heading"
    >
      <div className="landing-container">
        <div className="section-label-row">
          <span className="section-label-pill">Help</span>
        </div>
        <h2 className="landing-section-heading" id="faq-heading">
          Frequently Asked Questions
        </h2>
        <p className="landing-section-subheading">
          Answers are based on the actual system implementation.
        </p>

        <div className="faq-list" role="list">
          {FAQ_ITEMS.map((item) => (
            <FAQItem
              key={item.id}
              item={item}
              isOpen={openId === item.id}
              onToggle={() => toggle(item.id)}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export default FAQ;

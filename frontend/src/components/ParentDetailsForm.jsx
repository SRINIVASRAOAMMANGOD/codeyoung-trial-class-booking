// ParentDetailsForm.jsx — Captures parent contact and child details.

function ParentDetailsForm({ form, errors, onChange }) {
  return (
    <section className="card form-section" aria-labelledby="parent-details-heading">
      <h2 id="parent-details-heading" className="section-title">
        <span className="step-number">1</span> Parent & Student Details
      </h2>
      <p className="section-description">
        Enter your contact information and student name so we can set up the classroom.
      </p>

      <div className="form-group">
        <label htmlFor="parentName" className="form-label">
          Parent's Full Name <span className="required">*</span>
        </label>
        <input
          id="parentName"
          name="parentName"
          type="text"
          className={`form-input ${errors.parentName ? 'input-error' : ''}`}
          placeholder="e.g. Sarah Jenkins"
          value={form.parentName}
          onChange={(e) => onChange('parentName', e.target.value)}
          aria-invalid={Boolean(errors.parentName)}
          aria-describedby={errors.parentName ? 'parentName-error' : undefined}
          required
        />
        {errors.parentName && (
          <p id="parentName-error" className="field-error">
            {errors.parentName}
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="parentEmail" className="form-label">
          Parent's Email Address <span className="required">*</span>
        </label>
        <input
          id="parentEmail"
          name="parentEmail"
          type="email"
          className={`form-input ${errors.parentEmail ? 'input-error' : ''}`}
          placeholder="e.g. sarah.jenkins@example.com"
          value={form.parentEmail}
          onChange={(e) => onChange('parentEmail', e.target.value)}
          aria-invalid={Boolean(errors.parentEmail)}
          aria-describedby={errors.parentEmail ? 'parentEmail-error' : undefined}
          required
        />
        {errors.parentEmail && (
          <p id="parentEmail-error" className="field-error">
            {errors.parentEmail}
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="childName" className="form-label">
          Student's Name <span className="required">*</span>
        </label>
        <input
          id="childName"
          name="childName"
          type="text"
          className={`form-input ${errors.childName ? 'input-error' : ''}`}
          placeholder="e.g. Leo Jenkins"
          value={form.childName}
          onChange={(e) => onChange('childName', e.target.value)}
          aria-invalid={Boolean(errors.childName)}
          aria-describedby={errors.childName ? 'childName-error' : undefined}
          required
        />
        {errors.childName && (
          <p id="childName-error" className="field-error">
            {errors.childName}
          </p>
        )}
      </div>
    </section>
  );
}

export default ParentDetailsForm;

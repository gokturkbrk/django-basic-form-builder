# Django Form Builder - Configuration Guide

Complete reference for all configuration options available in the Form Builder system.

---

## Table of Contents

1. [Custom Form Configuration](#custom-form-configuration)
2. [Form Field Configuration](#form-field-configuration)
3. [Field Types & Options](#field-types--options)
4. [Field Options (Dropdown/Radio/Checkbox)](#field-options-dropdownradiocheckbox)
5. [Advanced JSON Configuration](#advanced-json-configuration)

---

## Custom Form Configuration

### Basic Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **Name** | Text | Yes | Display name of the form (e.g., "Customer Feedback Form") |
| **Slug** | Slug | Yes | URL-friendly identifier (auto-generated from name) |
| **Description** | Textarea | No | Optional description of the form's purpose |
| **Status** | Choice | Yes | `draft` or `published` - Controls form visibility |

### Behavior

- **Schema Generation**: JSON schema is automatically generated when form fields are saved
- **Publishing**: Set status to "published" to make the form active
- **Preview**: Use the "Preview JSON Schema" button to see the generated schema

---

## Form Field Configuration

### Common Fields (All Field Types)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **Label** | Text | Yes | Short label shown in forms (e.g., "Email", "Age", "Country") |
| **Slug** | Slug | Yes | Field identifier used in data submission (auto-generated) |
| **Question** | Textarea | No | Detailed question/explanation shown to users (e.g., "What is your email address?") |
| **Field Type** | Dropdown | Yes | Type of input field (see Field Types below) |
| **Position** | Number | Yes | Display order (auto-updated when adding/removing fields) |
| **Required** | Checkbox | No | Whether the field must be filled by users |

### Display Options (All Field Types)

| Field | Type | Description |
|-------|------|-------------|
| **Placeholder** | Text | Hint text shown inside empty input fields (e.g., "Enter your name") |
| **Default Value** | Text | Pre-filled value when form loads |
| **Help Text** | Text | Additional guidance shown below the field |

### Usage Guidelines

- **Label vs Question**: Use **Label** for short field names (1-3 words). Use **Question** for detailed descriptions or instructions.
- **Position**: Fields are displayed in ascending position order (1, 2, 3...). Position auto-updates when you add/remove fields.
- **Required Fields**: Mark important fields as required to ensure data completeness.

---

## Field Types & Options

### 1. Text Input (`text`)

Single-line text input for short responses.

**Use Cases**: Names, email addresses, phone numbers, URLs

**Configuration Options**:

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| **Min Length** | Integer | Minimum characters required | `2` (at least 2 characters) |
| **Max Length** | Integer | Maximum characters allowed | `100` (up to 100 characters) |

**Advanced Config (JSON)**:

```json
{
  "minLength": 2,
  "maxLength": 100,
  "pattern": "^[A-Za-z\\s]+$",
  "inputMode": "text",
  "prefix": "$",
  "suffix": ".00"
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `minLength` | int | Minimum character count |
| `maxLength` | int | Maximum character count |
| `pattern` | string | Regular expression for validation |
| `inputMode` | string | Keyboard hint: `text`, `email`, `tel`, `url` |
| `prefix` | string | Text shown before input (e.g., "$" for currency) |
| `suffix` | string | Text shown after input (e.g., "kg" for weight) |

---

### 2. Number Input (`number`)

Numeric input with optional range and step controls.

**Use Cases**: Age, quantity, price, rating scores

**Configuration Options**:

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| **Min Value** | Float | Minimum allowed value | `0` (non-negative) |
| **Max Value** | Float | Maximum allowed value | `150` (age limit) |
| **Step** | Float | Increment/decrement step | `0.5` (half-unit steps) |

**Advanced Config (JSON)**:

```json
{
  "min": 0,
  "max": 150,
  "step": 1,
  "prefix": "$",
  "suffix": "USD",
  "unit": "kg"
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `min` | number | Minimum value constraint |
| `max` | number | Maximum value constraint |
| `step` | number | Increment step (e.g., 0.5 for decimals) |
| `prefix` | string | Display prefix (e.g., "$") |
| `suffix` | string | Display suffix (e.g., "USD") |
| `unit` | string | Unit of measurement (e.g., "kg", "lbs") |

---

### 3. Textarea (`textarea`)

Multi-line text input for longer responses.

**Use Cases**: Comments, feedback, descriptions, messages

**Configuration Options**:

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| **Min Length** | Integer | Minimum characters required | `10` |
| **Max Length** | Integer | Maximum characters allowed | `500` |

**Advanced Config (JSON)**:

```json
{
  "rows": 4,
  "minLength": 10,
  "maxLength": 500,
  "autoResize": true
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `rows` | int | Number of visible text rows (height) |
| `minLength` | int | Minimum character count |
| `maxLength` | int | Maximum character count |
| `autoResize` | bool | Auto-expand height as user types |

---

### 4. Dropdown (`dropdown`)

Single-select dropdown menu (or multi-select if configured).

**Use Cases**: Country selection, category selection, status

**Configuration**:

After saving the field, use the **"Add New Option"** button to add dropdown choices.

**Advanced Config (JSON)**:

```json
{
  "allowMultiple": false,
  "allowOther": true
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `allowMultiple` | bool | Enable multi-select mode (checkboxes in dropdown) |
| `allowOther` | bool | Add "Other" option with text input |

**Important**: Only **one option** can be marked as default for single-select dropdowns.

---

### 5. Radio Buttons (`radio`)

Single-choice selection displayed as radio buttons.

**Use Cases**: Gender, yes/no questions, satisfaction level

**Configuration**:

After saving the field, use the **"Add New Option"** button to add radio choices.

**Advanced Config (JSON)**:

```json
{
  "allowOther": true
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `allowOther` | bool | Add "Other" option with text input field |

**Important**: Only **one option** can be marked as default.

---

### 6. Checkboxes (`checkbox`)

Multiple-choice selection displayed as checkboxes.

**Use Cases**: Interests, preferences, opt-in options

**Configuration**:

After saving the field, use the **"Add New Option"** button to add checkbox choices.

**Advanced Config (JSON)**:

```json
{
  "minSelections": 1,
  "maxSelections": 3,
  "allowOther": true
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `minSelections` | int | Minimum number of checkboxes user must select |
| `maxSelections` | int | Maximum number of checkboxes user can select |
| `allowOther` | bool | Add "Other" option with text input |

**Note**: Checkboxes can have **multiple defaults** (unlike radio/dropdown).

---

### 7. Rating Scale (`rating`)

Visual rating input (stars, numbers, or emoji).

**Use Cases**: Satisfaction scores, quality ratings, NPS

**Configuration Options**:

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| **Rating Scale** | Dropdown | Choose scale size | `5` (5 stars) or `10` (10 points) |
| **Rating Style** | Dropdown | Visual style | `stars`, `numeric`, `emoji` |

**Advanced Config (JSON)**:

```json
{
  "scale": 5,
  "style": "stars",
  "minLabel": "Poor",
  "maxLabel": "Excellent"
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `scale` | int | Rating scale: `5` or `10` |
| `style` | string | Display style: `stars`, `numeric`, `emoji` |
| `minLabel` | string | Label for lowest rating (e.g., "Poor") |
| `maxLabel` | string | Label for highest rating (e.g., "Excellent") |

---

### 8. Boolean (`boolean`)

Yes/No or True/False selection.

**Use Cases**: Agreements, opt-ins, binary choices

**Advanced Config (JSON)**:

```json
{
  "trueLabel": "Yes, I agree",
  "falseLabel": "No, I disagree",
  "style": "toggle"
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `trueLabel` | string | Custom label for "true" option |
| `falseLabel` | string | Custom label for "false" option |
| `style` | string | Display style: `checkbox`, `toggle`, `radio` |

---

### 9. Email Address (`email`)

Email input with validation.

**Use Cases**: Contact email, notification preferences

**Advanced Config (JSON)**:

```json
{
  "confirmEmail": true
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `confirmEmail` | bool | Require user to enter email twice for confirmation |

---

### 10. Date Picker (`date`)

Date selection input.

**Use Cases**: Birth date, appointment date, event date

**Advanced Config (JSON)**:

```json
{
  "minDate": "2024-01-01",
  "maxDate": "2026-12-31",
  "format": "YYYY-MM-DD"
}
```

| JSON Key | Type | Description |
|----------|------|-------------|
| `minDate` | string | Earliest selectable date (YYYY-MM-DD) |
| `maxDate` | string | Latest selectable date (YYYY-MM-DD) |
| `format` | string | Date format string for display |

---

## Field Options (Dropdown/Radio/Checkbox)

Field Options are the individual choices available for dropdown, radio button, and checkbox fields.

### Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **Field** | Foreign Key | Yes | Parent field (automatically set when using "Add New Option" button) |
| **Value** | Text | Yes | Internal value stored in database (e.g., "us", "ca", "uk") |
| **Label** | Text | Yes | User-facing display text (e.g., "United States", "Canada") |
| **Position** | Integer | Yes | Display order within the field |
| **Is Default** | Boolean | No | Mark this option as pre-selected |

### Best Practices

1. **Value vs Label**:
   - **Value**: Use short, lowercase, hyphen-separated codes (e.g., "united-states", "5-stars")
   - **Label**: Use friendly, readable text (e.g., "United States", "5 Stars")

2. **Position**:
   - Options are displayed in ascending position order (1, 2, 3...)
   - You can edit positions in the list view to reorder options

3. **Default Selection**:
   - **Radio/Dropdown**: Only ONE option can be default
   - **Checkbox**: Multiple options can be default
   - Use the "Set selected option as default" action in the list view

### Example Option Set

For a "Country" dropdown field:

| Value | Label | Position | Is Default |
|-------|-------|----------|------------|
| `us` | United States | 1 | Yes |
| `ca` | Canada | 2 | No |
| `uk` | United Kingdom | 3 | No |
| `de` | Germany | 4 | No |

---

## Advanced JSON Configuration

For advanced users, the **Advanced Configuration** section allows direct JSON input for fine-grained control.

### Configuration Format

```json
{
  "key1": value1,
  "key2": value2
}
```

### Field-Specific Attributes

The system validates that only relevant attributes are used for each field type. Invalid keys will be rejected with an error message.

#### Text Field Config

```json
{
  "minLength": 2,
  "maxLength": 100,
  "pattern": "^[A-Za-z\\s]+$",
  "inputMode": "text",
  "prefix": "Mr.",
  "suffix": ""
}
```

#### Number Field Config

```json
{
  "min": 0,
  "max": 999.99,
  "step": 0.01,
  "prefix": "$",
  "suffix": " USD",
  "unit": "dollars"
}
```

#### Textarea Field Config

```json
{
  "rows": 6,
  "minLength": 50,
  "maxLength": 1000,
  "autoResize": true
}
```

#### Dropdown Field Config

```json
{
  "allowMultiple": false,
  "allowOther": true
}
```

#### Radio Field Config

```json
{
  "allowOther": true
}
```

#### Checkbox Field Config

```json
{
  "minSelections": 2,
  "maxSelections": 5,
  "allowOther": false
}
```

#### Rating Field Config

```json
{
  "scale": 10,
  "style": "numeric",
  "minLabel": "Not at all likely",
  "maxLabel": "Extremely likely"
}
```

#### Boolean Field Config

```json
{
  "trueLabel": "I accept the terms",
  "falseLabel": "I do not accept",
  "style": "checkbox"
}
```

#### Email Field Config

```json
{
  "confirmEmail": true
}
```

#### Date Field Config

```json
{
  "minDate": "1900-01-01",
  "maxDate": "2030-12-31",
  "format": "MM/DD/YYYY"
}
```

---

## Common Workflows

### Creating a Feedback Form

1. **Create Custom Form**
   - Name: "Customer Feedback Survey"
   - Status: Draft (change to Published when ready)

2. **Add Text Field** (Name)
   - Label: "Name"
   - Question: "What is your full name?"
   - Required: Yes
   - Min Length: 2

3. **Add Email Field** (Contact)
   - Label: "Email"
   - Question: "How can we reach you?"
   - Required: Yes

4. **Add Rating Field** (Satisfaction)
   - Label: "Satisfaction"
   - Question: "How satisfied are you with our service?"
   - Rating Scale: 5
   - Rating Style: stars
   - Required: Yes

5. **Add Radio Field** (Recommend)
   - Label: "Recommend"
   - Question: "Would you recommend us to others?"
   - Add Options:
     - "yes" → "Yes, definitely"
     - "maybe" → "Maybe"
     - "no" → "No"
   - Required: Yes

6. **Add Textarea Field** (Comments)
   - Label: "Comments"
   - Question: "Any additional feedback?"
   - Min Length: 10
   - Max Length: 500
   - Required: No

7. **Publish Form**
   - Set Status to "Published"
   - Use "Preview JSON Schema" to verify configuration

---

## Validation Rules

### Automatic Validations

1. **Number Fields**: Max must be greater than Min
2. **Text/Textarea**: MaxLength must be greater than MinLength
3. **Field Options**: 
   - Unique values per field
   - Unique positions per field
   - Only for dropdown/radio/checkbox types
   - Single default for radio/dropdown
4. **Required Fields**: Slug must be unique per form

### Error Messages

The system provides clear validation errors when:
- Invalid configuration is provided
- Constraints are violated (e.g., min > max)
- Options are added to unsupported field types
- Multiple defaults are set for single-select fields

---

## Tips & Best Practices

### Form Design

1. **Keep forms short**: 5-10 fields maximum for best completion rates
2. **Group related fields**: Use field positions to create logical sections
3. **Use clear labels**: Short, descriptive labels work best
4. **Add help text**: Clarify complex or unusual questions

### Field Configuration

1. **Text fields**: Set reasonable length limits to prevent abuse
2. **Required fields**: Only mark truly essential fields as required
3. **Default values**: Use sparingly - let users provide their own input
4. **Validation**: Use Min/Max constraints to ensure data quality

### Options Management

1. **Ordering**: Put most common options first (position 1, 2, 3...)
2. **Labels**: Use clear, unambiguous text
3. **Values**: Use consistent naming (lowercase-with-hyphens)
4. **Defaults**: Choose sensible defaults for better UX

### Testing

1. **Preview schema**: Always check the JSON schema before publishing
2. **Test with data**: Try submitting test responses
3. **Validate constraints**: Ensure min/max rules work as expected
4. **Mobile-friendly**: Consider how fields appear on mobile devices

---

## Troubleshooting

### "Position not updating"
- Positions auto-update when you add/remove fields
- Refresh the page if positions seem incorrect

### "Can't add options"
- Options only work for dropdown, radio, and checkbox fields
- Save the field first, then use "Add New Option" button

### "Multiple defaults error"
- Radio and dropdown fields support only one default
- Use the "Set selected option as default" action to change defaults
- Checkboxes can have multiple defaults

### "Validation error when saving"
- Check that Min < Max for number fields
- Ensure MinLength < MaxLength for text fields
- Verify JSON syntax in Advanced Configuration section

---

## API Schema Output

The form builder generates a JSON schema that can be used by frontend applications:

```json
{
  "form": {
    "slug": "customer-feedback",
    "name": "Customer Feedback Survey",
    "description": "Help us improve our service"
  },
  "fields": [
    {
      "slug": "name",
      "label": "Name",
      "question": "What is your full name?",
      "type": "text",
      "required": true,
      "position": 1,
      "config": {
        "minLength": 2,
        "maxLength": 100
      }
    },
    {
      "slug": "rating",
      "label": "Satisfaction",
      "question": "How satisfied are you?",
      "type": "rating",
      "required": true,
      "position": 2,
      "config": {
        "scale": 5,
        "style": "stars"
      }
    }
  ]
}
```

This schema can be consumed by any frontend framework to render dynamic forms.

---

## Support

For questions or issues:
1. Check this guide first
2. Review the inline help text in the admin interface
3. Examine the generated JSON schema for debugging
4. Test with simple configurations before adding complexity

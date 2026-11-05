# frozen_string_literal: true

# The new pricer. It prices lines with the tax rate that it is given.
class PricingEngine
  def initialize(tax_percent:)
    @tax_percent = tax_percent
  end

  def price(lines)
    subtotal = lines.sum { |line| line.unit_pence * line.quantity }
    subtotal + (subtotal * @tax_percent / 100)
  end
end

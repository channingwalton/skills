# frozen_string_literal: true

require_relative "legacy_pricer"

class TaxReport
  def heading
    "VAT at #{LegacyPricer::TAX_PERCENT}%"
  end
end
